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
        if file.is_file() and file.suffix in ('.txt','.mod'):
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
    report={'ok':True,'parsed_script_files':len(checked),'population_algorithm_cases':count,'randomized_monthly_steps':19200,'localisation_languages':2,'engine_loading_verified':False,'employment_allocation_verified':False,'in_game_tests_passed':False}
    print(json.dumps(report,ensure_ascii=False))
    return report

if __name__=='__main__': validate()
