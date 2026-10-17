"""Derive scoped dual-ascension exceptions from installed 4.5.2 definitions.

This module contains original transformation logic only. Its generated native
definitions stay in the local installed mod and must never be redistributed.
"""
from pathlib import Path
from copy import deepcopy
from validate_mod import parse

PERMISSION='haipam_can_dual_ascend'

def render(nodes,indent=0):
    lines=[]
    for node in nodes:
        if isinstance(node,str):lines.append(' '*indent+node);continue
        key,op,value=node
        if isinstance(value,list):
            lines.append(' '*indent+key+' '+op+' {')
            lines.append(render(value,indent+1));lines.append(' '*indent+'}')
        else:lines.append(' '*indent+key+' '+op+' '+value)
    return '\n'.join(lines)

def rewrite_condition(nodes,cross_checks):
    """NOR/NOT block only non-permitted countries; positive prerequisites allow
    the permitted dual path. Every other leaf and condition is preserved."""
    out=[];count=0
    for node in nodes:
        if not isinstance(node,tuple):out.append(node);continue
        key,op,value=node
        if not isinstance(value,list) and op=='=' and (key,value) in cross_checks:
            if value in ('yes','ap_mind_over_matter','ap_engineered_evolution'):
                out.append(('AND','=',[node,('NOT','=',[(PERMISSION,'=','yes')])]))
            else: # a native has_psionic_ascension = no prerequisite
                out.append(('OR','=',[node,(PERMISSION,'=','yes')]))
            count+=1
        elif isinstance(value,list):
            transformed,n=rewrite_condition(value,cross_checks)
            out.append((key,op,transformed));count+=n
        else:out.append(node)
    return out,count

def unexception(nodes):
    """Verify that removing the new exception reconstructs the original AST."""
    out=[]
    for node in nodes:
        if isinstance(node,tuple) and isinstance(node[2],list):
            key,op,value=node
            if key=='AND' and len(value)==2 and value[1]==('NOT','=',[(PERMISSION,'=','yes')]):
                out.append(value[0])
            elif key=='OR' and len(value)==2 and value[1]==(PERMISSION,'=','yes'):
                out.append(value[0])
            else:out.append((key,op,unexception(value)))
        else:out.append(node)
    return out

def make_adapters(game):
    result={};patched=0
    ap_path=game/'common/ascension_perks/00_ascension_paths.txt'
    ap=parse(ap_path.read_text(encoding='utf-8-sig'))
    exports=[node for node in ap if isinstance(node,tuple) and node[0].startswith('@')]
    for node in ap:
        if not isinstance(node,tuple) or node[0] not in ('ap_engineered_evolution','ap_mind_over_matter'):continue
        checks={('has_ascension_perk','ap_mind_over_matter'),('has_psionic_ascension','yes'),('has_psionic_ascension','no')} if node[0]=='ap_engineered_evolution' else {('has_ascension_perk','ap_engineered_evolution')}
        body=[]
        for field in node[2]:
            if isinstance(field,tuple) and field[0] in ('potential','possible'):
                changed,count=rewrite_condition(field[2],checks)
                assert unexception(changed)==field[2]
                body.append((field[0],field[1],changed));patched+=count
            else:body.append(deepcopy(field))
        exports.append((node[0],node[1],body))
    assert len([n for n in exports if not n[0].startswith('@')])==2
    result['common/ascension_perks/zz_haipam_dual_ascension.txt']=render(exports)+'\n'

    for filename in ['01_genetics.txt','01_cloning.txt','01_purity.txt','01_mutation.txt','01_psionics.txt','01_psionics_shroud.txt']:
        path=game/'common/tradition_categories'/filename
        source=parse(path.read_text(encoding='utf-8-sig'));output=[];changes=0
        if filename in ('01_psionics.txt','01_psionics_shroud.txt'):
            checks={(key,'yes') for key in ['has_genetic_ascension','has_purity_ascension','has_cloning_ascension','has_mutation_ascension']}
        else:checks={('has_psionic_ascension','yes'),('has_psionic_ascension','no')}
        for node in source:
            if isinstance(node,tuple) and isinstance(node[2],list):
                body=[]
                for field in node[2]:
                    if isinstance(field,tuple) and field[0]=='potential':
                        changed,count=rewrite_condition(field[2],checks)
                        assert unexception(changed)==field[2]
                        body.append((field[0],field[1],changed));changes+=count
                    else:body.append(deepcopy(field))
                output.append((node[0],node[1],body))
            else:output.append(deepcopy(node))
        assert changes>0,'No expected native exclusion found in '+filename
        result['common/tradition_categories/zz_haipam_dual_'+filename]=render(output)+'\n';patched+=changes
    assert patched==16, 'Native cross-path conditions changed; inspect game version before installing'
    for text in result.values():parse(text)
    return {path:'# LOCALLY GENERATED from installed 4.5.2. Do not redistribute.\n'+text for path,text in result.items()}

def logic_tests():
    checks={('has_ascension_perk','ap_engineered_evolution'),('has_psionic_ascension','yes'),('has_psionic_ascension','no')}
    def evaluate(nodes,permission,selected,synthetic=False):
        answers=[]
        for key,op,value in nodes:
            if key=='AND':answer=evaluate(value,permission,selected,synthetic)
            elif key=='OR':answer=any(evaluate([child],permission,selected,synthetic) for child in value)
            elif key=='NOR':answer=not any(evaluate([child],permission,selected,synthetic) for child in value)
            elif key=='NOT':answer=not evaluate(value,permission,selected,synthetic)
            elif key==PERMISSION:answer=permission
            elif key=='has_psionic_ascension':answer=selected if value=='yes' else not selected
            elif key=='has_ascension_perk':answer=synthetic if value=='ap_synthetic_evolution' else selected
            else:raise AssertionError(key)
            answers.append(answer)
        return all(answers)
    examples=[ [('NOR','=',[('has_ascension_perk','=','ap_engineered_evolution'),('has_ascension_perk','=','ap_synthetic_evolution')])],
               [('NOT','=',[('has_ascension_perk','=','ap_engineered_evolution')])],
               [('has_psionic_ascension','=','no')] ]
    count=0
    for original in examples:
        changed,_=rewrite_condition(original,checks);assert unexception(changed)==original
        for permission in (False,True):
            for selected in (False,True):
                for synthetic in (False,True):
                    answer=evaluate(changed,permission,selected,synthetic)
                    if not permission:assert answer==evaluate(original,permission,selected,synthetic)
                    elif original==examples[0]:assert answer==(not synthetic)
                    else:assert answer
                    count+=1
    return count

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path);a=p.parse_args()
    report={'logic_cases':logic_tests(),'engine_verified':False}
    if a.game:report['local_adapter_files']=len(make_adapters(a.game))
    print(json.dumps(report))
