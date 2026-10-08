"""Preserve CLI process overrides when Bambu Studio opens a sliced 3MF.

The GUI refreshes unlisted options from its system preset. Raw project values
alone therefore do not preserve our CLI profile changes. See Bambu's
PresetBundle.cpp load_config_file_config and Preset.cpp load_external_preset.
This helper changes settings metadata/config comments, never toolpath moves.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import tempfile
import zipfile

PROCESS_OVERRIDE_KEYS = (
    'wall_loops', 'enable_support', 'support_on_build_plate_only',
    'support_type', 'sparse_infill_density', 'sparse_infill_pattern',
    'brim_width', 'brim_type', 'enable_prime_tower',
)
SETTINGS_ENTRY = 'Metadata/project_settings.config'
OVERRIDE_KEY = 'different_settings_to_system'
CONFIG_BLOCK = re.compile(rb'^; CONFIG_BLOCK_START\r?\n.*?^; CONFIG_BLOCK_END\r?\n?', re.M | re.S)


def _scalar(value):
    if isinstance(value, bool):
        return str(int(value))
    assert isinstance(value, (str, int, float)), f'Expected scalar process option, got {value!r}'
    return str(value)


def _cstyle_strings(values):
    # Quote nonempty slots so internal semicolons remain inside that slot.
    # Bambu's unescape_strings_cstyle accepts quoted strings and backslash escapes.
    return ';'.join('"' + value.replace('\\', '\\\\').replace('"', '\\"')
                    .replace('\r', '\\r').replace('\n', '\\n') + '"'
                    if value else '' for value in values)


def _unescape_cstyle_strings(value):
    # Parse the same semicolon-separated/quoted representation for verification.
    result = []
    i = 0
    while True:
        while i < len(value) and value[i] in ' \t':
            i += 1
        chars = []
        if i < len(value) and value[i] == '"':
            i += 1
            while i < len(value) and value[i] != '"':
                char = value[i]
                if char == '\\':
                    i += 1
                    assert i < len(value), 'Incomplete C-style escape'
                    char = {'n': '\n', 'r': '\r'}.get(value[i], value[i])
                chars.append(char)
                i += 1
            assert i < len(value), 'Unterminated C-style string'
            i += 1
            while i < len(value) and value[i] in ' \t':
                i += 1
        else:
            while i < len(value) and value[i] != ';':
                chars.append(value[i])
                i += 1
        result.append(''.join(chars))
        if i == len(value):
            return result
        assert value[i] == ';', 'Invalid C-style string separator'
        i += 1


def _config_values(gcode):
    blocks = list(CONFIG_BLOCK.finditer(gcode))
    assert len(blocks) == 1, 'Expected one exported G-code config block'
    block = blocks[0]
    values = {}
    for key, value in re.findall(rb'^; ([a-z0-9_]+) = ([^\r\n]*)\r?$', block.group(), re.M):
        key = key.decode('ascii')
        assert key not in values, f'Duplicate G-code config option: {key}'
        values[key] = value.decode('utf-8')
    return values, block


def preserve_process_overrides(project, expected_process=None):
    """Repair an exported 3MF atomically and verify settings against its G-code.

    Preserve existing process overrides and every filament/printer override slot.
    Optional expected_process checks the actual slice against its input profile.
    Return a report suitable for the builders' existing result JSON files.
    """
    project = Path(project)
    with zipfile.ZipFile(project) as archive:
        infos = archive.infolist()
        assert len({info.filename for info in infos}) == len(infos), 'Duplicate ZIP entry'
        original = {info.filename: archive.read(info.filename) for info in infos}
        archive_comment = archive.comment
    settings = json.loads(original[SETTINGS_ENTRY])
    slots = settings.get(OVERRIDE_KEY)
    assert isinstance(slots, list) and len(slots) >= 3 and all(isinstance(v, str) for v in slots), 'Invalid preset override slots'
    assert len(slots) == len(settings['filament_colour']) + 2, 'Override slot count does not match filament count'
    original_other_slots = slots[1:]
    existing_keys = [key for key in slots[0].split(';') if key]
    assert all(re.fullmatch(r'[a-z0-9_]+', key) for key in existing_keys), 'Invalid process override key'
    override_keys = list(dict.fromkeys(existing_keys + list(PROCESS_OVERRIDE_KEYS)))
    settings[OVERRIDE_KEY] = [';'.join(override_keys), *original_other_slots]
    values = {key: _scalar(settings[key]) for key in PROCESS_OVERRIDE_KEYS}
    if expected_process is not None:
        for key, value in values.items():
            assert value == _scalar(expected_process[key]), f'Exported {key} differs from input process profile'
    serialized_slots = _cstyle_strings(settings[OVERRIDE_KEY])
    assert _unescape_cstyle_strings(serialized_slots) == settings[OVERRIDE_KEY]

    replacement = dict(original)
    replacement[SETTINGS_ENTRY] = (json.dumps(settings, indent=2) + '\n').encode('utf-8')
    gcodes = [name for name in original if re.fullmatch(r'Metadata/plate_\d+\.gcode', name)]
    assert gcodes, 'Project contains no sliced plate G-code'
    plate_checks = []
    for name in gcodes:
        gcode = original[name]
        config, block = _config_values(gcode)
        for key, value in values.items():
            assert config.get(key) == value, f'{name}: G-code {key} differs from project settings'
        assert OVERRIDE_KEY in config, f'{name}: missing G-code override metadata'
        md5_name = name + '.md5'
        assert original[md5_name].decode('ascii').strip().lower() == hashlib.md5(gcode).hexdigest(), f'{name}: existing G-code MD5 mismatch'
        pattern = re.compile(rb'^; different_settings_to_system = [^\r\n]*', re.M)
        new_block, count = pattern.subn(lambda _: b'; different_settings_to_system = ' + serialized_slots.encode('utf-8'), block.group())
        assert count == 1
        updated = gcode[:block.start()] + new_block + gcode[block.end():]
        new_config, new_bounds = _config_values(updated)
        assert {key: new_config[key] for key in PROCESS_OVERRIDE_KEYS} == values
        assert _unescape_cstyle_strings(new_config[OVERRIDE_KEY]) == settings[OVERRIDE_KEY]
        outside = gcode[:block.start()] + gcode[block.end():]
        assert updated[:new_bounds.start()] + updated[new_bounds.end():] == outside, 'Changed content outside config block'
        replacement[name] = updated
        replacement[md5_name] = hashlib.md5(updated).hexdigest().upper().encode('ascii')
        plate_checks.append({'plate': name, 'settings_match_gcode': True,
                             'override_slots_match_gcode': True,
                             'outside_config_block_sha256': hashlib.sha256(outside).hexdigest(),
                             'gcode_md5': replacement[md5_name].decode('ascii')})

    changed = [name for name in original if replacement[name] != original[name]]
    if changed:
        descriptor, temporary_name = tempfile.mkstemp(prefix=project.stem + '.', suffix='.tmp', dir=project.parent)
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            with zipfile.ZipFile(temporary, 'w') as archive:
                archive.comment = archive_comment
                for info in infos:
                    archive.writestr(info, replacement[info.filename])
            with zipfile.ZipFile(temporary) as archive:
                assert archive.testzip() is None, 'Repackaged archive failed CRC validation'
                assert archive.namelist() == list(original), 'Changed archive entry order'
                for name, data in replacement.items():
                    assert archive.read(name) == data, f'Repackaged entry mismatch: {name}'
                saved = json.loads(archive.read(SETTINGS_ENTRY))
                assert saved[OVERRIDE_KEY][1:] == original_other_slots
            os.replace(temporary, project)
        finally:
            if temporary.exists():
                temporary.unlink()
    return {'project': str(project), 'process_override_keys': override_keys,
            'process_values': values, 'other_profile_override_slots_preserved': True,
            'changed_entries': changed, 'plate_checks': plate_checks,
            'project_sha256': hashlib.sha256(project.read_bytes()).hexdigest(), 'passed': True}


if __name__ == '__main__':
    import sys
    assert len(sys.argv) == 2, 'Usage: python tools/bambu_project_settings.py PROJECT.3mf'
    print(json.dumps(preserve_process_overrides(sys.argv[1]), indent=2))
