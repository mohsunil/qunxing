"""Check dependency wiring, optionally against the user's installed game.

These checks resolve definition names, not engine scopes or gameplay behavior.
No native game content is copied into the package or the report.
"""
import argparse,json,re
from pathlib import Path
from validate_mod import parse,fields,MOD

def texts(folder,suffix='.txt'):
    return '\n'.join(p.read_text(encoding='utf-8-sig') for p in folder.rglob('*'+suffix))
def keys(text):
    return set(re.findall(r'^([A-Za-z0-9_]+)\s*=\s*\{',text,re.M))
def validate(game=None):
    tech_source=texts(MOD/'common/technology')
    techs=keys(tech_source)
    all_source=texts(MOD)
    prerequisites=set()
    for body in re.findall(r'prerequisites\s*=\s*\{([^}]+)\}',all_source):
        prerequisites.update(re.findall(r'"(tech_[^"]+)"',body))
    assert len(techs)==11
    ships=fields(parse(texts(MOD/'common/ship_sizes')))
    components={}
    for node in parse(texts(MOD/'common/component_templates')):
        if isinstance(node,tuple):
            value=fields(node[2]);components[value['key'].strip('"')]=value
    sections={}
    for _,_,node in parse(texts(MOD/'common/section_templates')):
        value=fields(node);sections[value['key'].strip('"')]=value
        assert value['ship_size'] in ships
        slots=fields(fields(ships[value['ship_size']])['section_slots'])
        assert '"'+value['fits_on_slot']+'"' in slots
    designs=parse(texts(MOD/'common/global_ship_designs'))
    native_components=set()
    if game:
        native_techs=keys(texts(game/'common/technology'))
        missing=prerequisites-techs-native_techs
        assert not missing, 'Missing technology dependencies: '+str(sorted(missing))
        native_components=set(re.findall(r'\bkey\s*=\s*"([^"]+)"',texts(game/'common/component_templates')))
        native_gfx=texts(game/'interface','.gfx')
        gfx_defined=set(re.findall(r'\bname\s*=\s*"(GFX_[^"]+)"',native_gfx+texts(MOD/'interface','.gfx')))
        gfx_used=set(re.findall(r'\b(?:icon|picture|portrait)\s*=\s*"?(GFX_[A-Za-z0-9_]+)',all_source))
        assert not gfx_used-gfx_defined,'Missing GFX references: '+str(sorted(gfx_used-gfx_defined))
        native_jobs=keys(texts(game/'common/pop_jobs'))
        used_jobs=set(re.findall(r'\bjob_([A-Za-z0-9_]+)_add\s*=',all_source))
        assert not used_jobs-native_jobs,'Missing job definitions: '+str(sorted(used_jobs-native_jobs))
    for _,_,design in designs:
        data=fields(design);assert data['ship_size'] in ships
        for key,_,value in design:
            if key=='required_component' and game:
                assert value.strip('"') in set(components)|native_components
            if key=='section':
                section=fields(value);template=sections[section['template'].strip('"')]
                for k,_,v in value:
                    if k=='component' and game:
                        assert fields(v)['template'].strip('"') in set(components)|native_components
    ids=re.findall(r'\bid\s*=\s*(haipam\.\d+)',all_source)
    declared=[]
    for p in (MOD/'events').glob('*.txt'):
        for node in parse(p.read_text(encoding='utf-8')):
            if isinstance(node,tuple) and isinstance(node[2],list):declared.append(fields(node[2])['id'])
    assert len(declared)==len(set(declared)), 'Duplicate event definitions'
    assert not set(ids)-set(declared),'Unresolved event references'
    for language in ['english','simp_chinese']:
        loc_keys=[]
        for p in (MOD/'localisation'/language).glob('*.yml'):
            loc_keys+=re.findall(r'^ (\S+):0',p.read_text(encoding='utf-8-sig'),re.M)
        assert len(loc_keys)==len(set(loc_keys)),'Duplicate localization across files'
        assert techs<=set(loc_keys)
        assert set(ships)<=set(loc_keys)
    # Refits use ordinary capacity and upkeep. A recovered ship cannot opt out.
    assert 'uses_naval_capacity = no' not in texts(MOD/'events')
    assert 'damage = { min =' in texts(MOD/'common/component_templates')
    for key in ['HAIPAM_SMALL_AXIAL_PLASMA','HAIPAM_MEDIUM_AXIAL_PLASMA','HAIPAM_LARGE_AXIAL_PLASMA']:
        assert components[key].get('prerequisites'), 'Weapon tech gate missing'
    for key in ['HAIPAM_LIGHT_REACTOR','HAIPAM_MEDIUM_REACTOR','HAIPAM_HEAVY_REACTOR','HAIPAM_THRUSTER']:
        assert 'prerequisites' not in components[key], 'Required initial design component is tech-locked'
    assert 'min_damage =' not in texts(MOD/'common/component_templates')
    assert 'cooldown =' not in texts(MOD/'common/component_templates')
    assert 'allow = { alloys >=' not in texts(MOD/'events')
    arsenal=texts(MOD/'common/megastructures')
    assert 'has_planet_flag = haipam_homeworld' in arsenal
    assert 'destroy_colony' not in arsenal and 'change_pc' not in arsenal
    report={'ok':True,'technology_definitions':len(techs),'technology_dependencies':len(prerequisites),
            'ship_sizes':len(ships),'components':len(components),'sections':len(sections),
            'event_definitions':len(declared),'native_reference_check':bool(game),
            'engine_scopes_verified':False,'gameplay_verified':False}
    print(json.dumps(report));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path);a=p.parse_args();validate(a.game)
