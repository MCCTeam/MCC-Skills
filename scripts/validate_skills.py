#!/usr/bin/env python3
"""Check installable skill metadata and bundled references."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors = []
names = set()
skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
if not skills:
    errors.append('No skills found')
for entry in skills:
    text = entry.read_text(encoding='utf-8')
    front = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
    if not front:
        errors.append(f'{entry.relative_to(ROOT)}: missing YAML frontmatter')
        continue
    metadata = front[1]
    name = re.search(r'^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$', metadata, re.M)
    if not name or len(name[1]) > 64:
        errors.append(f'{entry.relative_to(ROOT)}: invalid name')
    elif name[1] != entry.parent.name or name[1] in names:
        errors.append(f'{entry.relative_to(ROOT)}: duplicate or mismatched name')
    else:
        names.add(name[1])
    if not re.search(r'^description:\s*\S', metadata, re.M):
        errors.append(f'{entry.relative_to(ROOT)}: missing description')
    for page in entry.parent.rglob('*.md'):
        contents = re.sub(r'```[^\n]*\n.*?```', '', page.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^\n)]+)\)', contents):
            target = target.strip().split(' "')[0].strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = (page.parent / unquote(parsed.path)).resolve()
            if not path.is_relative_to(entry.parent.resolve()):
                errors.append(f'{page.relative_to(ROOT)}: reference leaves skill: {target}')
            elif not path.exists():
                errors.append(f'{page.relative_to(ROOT)}: missing reference: {target}')
    if entry.parent.name in ('beacon-scripting', 'dmcbk-plugin-authoring', 'dmcbk-marketplace-authoring'):
        if len(text.splitlines()) > 500:
            errors.append(f'{entry.relative_to(ROOT)}: entry exceeds 500 lines')
        for page in entry.parent.rglob('*.md'):
            contents = page.read_text(encoding='utf-8')
            if re.search(r'https?://github\.com/MCCTeam/(?:DMCBK|Minecraft-Console-Client)/(?:blob|tree)/', contents):
                errors.append(f'{page.relative_to(ROOT)}: source repository dependency')
            if re.search(r'/home/anon/|/tmp/dmcbk|\b\.mcc\b', contents):
                errors.append(f'{page.relative_to(ROOT)}: nonportable research path or obsolete extension')

for page in (ROOT / 'README.md', ROOT / 'docs/validation.md'):
    if not page.exists():
        continue
    contents = re.sub(r'```[^\n]*\n.*?```', '', page.read_text(), flags=re.S)
    for target in re.findall(r'!?\[[^\]\n]*\]\(([^\n)]+)\)', contents):
        parsed = urlsplit(target)
        if not parsed.scheme and parsed.path and not (page.parent / unquote(parsed.path)).exists():
            errors.append(f'{page.relative_to(ROOT)}: missing reference: {target}')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'Validated {len(skills)} skill entries and their bundled references.')
