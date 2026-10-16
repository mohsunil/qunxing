"""Install only Haipam files; derive small compatibility rules from user's game.

No original game files are altered or distributed. Other mods/settings are untouched.
"""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def extract_block(text, name):
    match = re.search(r'^'+re.escape(name)+r'\s*=\s*\{', text, re.M)
    if not match:
        raise ValueError('Missing game rule: '+name)
    start = match.end()
    depth, quote, comment, escape = 1, False, False, False
    for i in range(start, len(text)):
        c = text[i]
        if comment:
            if c == '\n': comment = False
            continue
        if quote:
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == '"': quote = False
            continue
        if c == '#': comment = True
        elif c == '"': quote = True
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return text[start:i]
    raise ValueError('Unbalanced game rule '+name)

def make_adapter(game):
    settings = json.loads((game/'launcher-settings.json').read_text(encoding='utf-8-sig'))
    if settings.get('rawVersion') != 'v4.5.2':
        raise ValueError('Prototype supports v4.5.2 only; found '+str(settings.get('rawVersion')))
    source = (game/'common/game_rules/00_rules.txt').read_text(encoding='utf-8-sig')
    white_guard = 'OR = { root = { NOT = { has_valid_civic = civic_haipam_royal_biology } } has_trait = trait_haipam_white }'
    growth_guard = 'OR = { root.owner = { NOT = { has_valid_civic = civic_haipam_royal_biology } } NOT = { has_trait = trait_haipam_gray } }'
    ruler_guard = 'OR = { owner = { NOT = { has_valid_civic = civic_haipam_royal_biology } } has_trait = trait_haipam_white }'
    guards = {
        'can_species_procreate': growth_guard,
        'species_uses_bonus_growth': growth_guard,
        'can_generate_leader_from_pop_group': white_guard,
        'can_generate_leader_from_species': white_guard,
        'can_generate_military_leader_from_pop_group': white_guard,
        'can_fill_ruler_job': ruler_guard,
    }
    blocks = []
    for name, guard in guards.items():
        body = extract_block(source, name)
        # Preserve every original condition. The added guard is true for other empires.
        blocks.append(name+' = {\n '+guard+'\n'+body+'\n}\n')
    return '# LOCALLY GENERATED from installed v4.5.2. Do not redistribute.\n'+'\n'.join(blocks)

def install(game, userdir):
    source = ROOT/'mod/haipam'
    adapter = make_adapter(game)  # Validate before any destination mutation.
    moddir = userdir/'mod'
    target = moddir/'haipam_early'
    descriptor = moddir/'haipam_early.mod'
    for path in (target, descriptor):
        if path.is_symlink(): raise ValueError('Refusing a symlink destination: '+str(path))
    backup = None
    if target.exists() or descriptor.exists():
        if target.exists() and not (target/'descriptor.mod').exists():
            raise ValueError('Destination is not a recognized Haipam mod')
        backup = ROOT/'local-backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True)
        if target.exists(): shutil.copytree(target, backup/'haipam_early')
        if descriptor.exists(): shutil.copy2(descriptor, backup/'haipam_early.mod')
    moddir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    rulepath = target/'common/game_rules/zz_haipam_local_rules.txt'
    rulepath.parent.mkdir(parents=True, exist_ok=True)
    rulepath.write_text(adapter,encoding='utf-8')
    descriptor.write_text((source/'descriptor.mod').read_text(encoding='utf-8')+'path="'+target.as_posix()+'"\n',encoding='utf-8')
    checked=[]
    for file in source.rglob('*'):
        if file.is_file():
            dest=target/file.relative_to(source)
            if file.read_bytes()!=dest.read_bytes(): raise ValueError('Copy verification failed: '+str(dest))
            checked.append(str(file.relative_to(source)))
    report={'installed':True,'version':'0.2.1-alpha','target':str(target),'descriptor':str(descriptor),'source_files_verified':len(checked),'local_rules':6,'game_files_modified':False,'other_mods_modified':False,'backup':str(backup) if backup else None,'gameplay_verified':False}
    (ROOT/'local-install-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--game',type=Path,required=True)
    parser.add_argument('--userdir',type=Path,required=True)
    args=parser.parse_args()
    install(args.game.resolve(),args.userdir.resolve())
