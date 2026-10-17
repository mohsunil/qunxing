"""Static source checks and interpreter tests of the actual hatching effects.

This does not emulate Stellaris employment, script scopes, or engine loading.
"""
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'mod/haipam'
TOKEN = re.compile(r'\s+|\#[^\n]*|"(?:\\.|[^"\\])*"|>=|<=|!=|[{}=<>]|[^\s{}=<>#"]+')

def parse(text):
    tokens=[]
    pos=0
    for match in TOKEN.finditer(text):
        if match.start()!=pos: raise ValueError('Invalid token at '+str(pos))
        pos=match.end()
        t=match.group()
        if not t.isspace() and not t.startswith('#'): tokens.append(t)
    if pos!=len(text): raise ValueError('Unterminated string')
    i=0
    def block(nested=False):
        nonlocal i
        out=[]
        while i<len(tokens):
            key=tokens[i]; i+=1
            if key=='}':
                if not nested: raise ValueError('Extra close brace')
                return out
            if i<len(tokens) and tokens[i] in ('=','>','<','>=','<=','!='):
                op=tokens[i]; i+=1
                if i>=len(tokens): raise ValueError('Missing value')
                value=tokens[i]; i+=1
                if value=='{': value=block(True)
                elif value=='}': raise ValueError('Missing assignment value')
                out.append((key,op,value))
            else: out.append(key)
        if nested: raise ValueError('Unclosed brace')
        return out
    return block()

def fields(nodes): return {k:v for k,op,v in nodes}

def simulation_tests():
    effects=fields(parse((MOD/'common/scripted_effects/haipam_population.txt').read_text()))
    cases=0
    for category in ('worker','specialist'):
        def run(free, variables):
            born=[]
            def number(value):
                try: return float(value)
                except ValueError: return variables.get(value,0)
            def predicate(nodes):
                values=fields(nodes)
                which=values['which']
                op=next(op for k,op,v in nodes if k=='value')
                a,b=variables.get(which,0),number(values['value'])
                return {'>':a>b,'<':a<b,'>=':a>=b,'<=':a<=b,'=':a==b,'!=':a!=b}[op]
            def execute(nodes):
                for key,op,value in nodes:
                    args=fields(value)
                    if key=='export_trigger_value_to_variable': variables[args['variable']]=free
                    elif key=='set_variable': variables[args['which']]=number(args['value'])
                    elif key=='change_variable': variables[args['which']]=variables.get(args['which'],0)+number(args['value'])
                    elif key=='multiply_variable': variables[args['which']]=variables.get(args['which'],0)*number(args['value'])
                    elif key=='create_pop_group': born.append(number(args['size']))
                    elif key=='if':
                        condition=fields(args['limit'])
                        if predicate(condition['check_variable']): execute([n for n in value if n[0]!='limit'])
                    else: raise ValueError('Unsupported effect in test interpreter: '+key)
            execute(effects['haipam_tick_'+category])
            return sum(born)
        v={}
        births=[run(700,v) for _ in range(5)]
        # Each monthly export must reflect existing employment; this isolated case
        # keeps vacancy fixed until the first cohort arrives on tick five.
        assert births==[0,0,0,0,700],births
        cases+=1
        v={}
        for _ in range(3): assert run(1200,v)==0
        assert run(0,v)==0
        assert run(0,v)==0
        assert all(v[f'hp_{category}_{n}']==0 for n in range(4))
        cases+=1
        v={}
        run(700,v)
        run(1000,v)
        assert run(1000,v)==0
        assert run(1000,v)==0
        assert run(1000,v)==700
        assert run(300,v)==300  # Later demand did not restart the older cohort.
        cases+=1
        rng=random.Random(281990)
        for _ in range(200):
            v={}
            for month in range(48):
                free=rng.randrange(0,4001)
                born=run(free,v)
                pending=sum(v[f'hp_{category}_{n}'] for n in range(4))
                assert 0<=born<=free
                assert 0<=pending<=free-born
                assert all(v[f'hp_{category}_{n}']>=0 for n in range(4))
            cases+=1
    return cases

def validate():
    checked=[]
    for file in MOD.rglob('*'):
        if file.is_file() and file.suffix in ('.txt','.mod','.gfx'):
            parse(file.read_text(encoding='utf-8-sig'))
            checked.append(file.relative_to(MOD).as_posix())
    for file in (MOD/'localisation').rglob('*.yml'):
        raw=file.read_bytes()
        assert raw.startswith(b'\xef\xbb\xbf'), 'Missing localisation BOM'
        keys=[]
        for line in raw.decode('utf-8-sig').splitlines()[1:]:
            match=re.fullmatch(r' (\S+):0 (".*")',line)
            assert match, 'Malformed localisation: '+line
            keys.append(match[1]); json.loads(match[2])
        assert len(keys)==len(set(keys))
    count=simulation_tests()
    # Regression guards from real 4.5.2 startup errors, not only grammar checks.
    empire=fields(parse((MOD/'prescripted_countries/haipam_empire.txt').read_text()))['haipam_early_empire']
    empire_fields=fields(empire)
    assert isinstance(empire_fields['playable'],str), 'Preset playable expects a scripted-trigger key'
    assert empire_fields['playable'] in fields(parse((MOD/'common/scripted_triggers/haipam_triggers.txt').read_text()))
    assert empire_fields['flag'] in fields(parse((MOD/'common/prescripted_flags/haipam_flags.txt').read_text()))
    assert ('trait','=','"trait_syncretic_proles"') in empire_fields['secondary_species']
    assert empire_fields['government']=='gov_star_empire'
    assert empire_fields['initializer']=='""', 'Internal random initializer cannot be selected in empire designer'
    gray_trait=fields(fields(parse((MOD/'common/traits/haipam_traits.txt').read_text()))['trait_haipam_gray'])
    assert gray_trait['initial']=='yes', 'Secondary lineage trait must be legal at empire creation'
    event_source=(MOD/'events/haipam_population_events.txt').read_text()
    assert 'planet_event = { id = haipam.20' not in event_source
    assert 'colony_event = { id = haipam.20' in event_source
    assert 'haipam_repair_gray_species = yes' in event_source
    repair=fields(parse((MOD/'common/scripted_effects/haipam_population.txt').read_text()))['haipam_repair_gray_species']
    assert 'change_species = event_target:haipam_gray_repaired' in (MOD/'common/scripted_effects/haipam_population.txt').read_text()
    assert 'haipam_is_gray_pop_group = yes' in event_source
    # Texture headers and references can be checked without graphics/Pillow on Cloud.
    import struct
    texture_sizes={}
    for file in MOD.rglob('*.dds'):
        header=file.read_bytes()[:128]
        assert header[:4]==b'DDS ' and len(header)==128
        height,width=struct.unpack_from('<II',header,12)
        assert width>0 and height>0
        texture_sizes[file.relative_to(MOD).as_posix()]=[width,height]
    assert texture_sizes['gfx/interface/portraits/haipam_white_01.dds']==[575,380]
    assert texture_sizes['gfx/interface/portraits/haipam_gray_01.dds']==[575,380]
    assert texture_sizes['gfx/interface/portraits/haipam_white_02.dds']==[575,380]
    assert texture_sizes['gfx/interface/portraits/haipam_gray_02.dds']==[575,380]
    assert texture_sizes['flags/haipam/haipam_royal_crest.dds']==[128,128]
    assert texture_sizes['flags/haipam/map/haipam_royal_crest.dds']==[256,256]
    assert texture_sizes['flags/haipam/small/haipam_royal_crest.dds']==[24,24]
    for file in MOD.rglob('*'):
        if file.is_file() and file.suffix in ('.txt','.gfx'):
            for path in re.findall(r'(?:texturefile|icon)\s*=\s*"(gfx/[^\"]+\.dds)"',file.read_text(encoding='utf-8')):
                assert (MOD/path).is_file(), 'Missing custom texture: '+path
    report={'ok':True,'parsed_script_files':len(checked),'population_algorithm_cases':count,'randomized_monthly_steps':19200,'engine_error_regression_guards':8,'localisation_languages':2,'engine_loading_verified':False,'employment_allocation_verified':False,'in_game_tests_passed':False}
    print(json.dumps(report,ensure_ascii=False))
    return report

if __name__=='__main__': validate()
