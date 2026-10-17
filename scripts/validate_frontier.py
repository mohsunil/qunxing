"""Execute actual frontier control-flow with abstract eligible world fixtures.

This checks costs/organization/branches, not engine scope resolution or AI wars.
"""
from pathlib import Path
from itertools import product
import json
from validate_mod import parse,fields,MOD

effects=fields(parse((MOD/'common/scripted_effects/haipam_frontier_effects.txt').read_text(encoding='utf-8')))
events={fields(v)['id']:fields(v) for k,op,v in parse((MOD/'events/haipam_frontier_events.txt').read_text(encoding='utf-8')) if k!='namespace'}
salvation_triggers=fields(parse((MOD/'common/scripted_triggers/haipam_salvation_triggers.txt').read_text(encoding='utf-8')))

class Fixture:
 def __init__(self,station=True,colony=True,temple=False):
  self.variables={};self.flags=set();self.resources={k:100000 for k in ['alloys','influence','energy','minerals','food','consumer_goods','unity']}
  self.station=station;self.colony=colony;self.temple=temple;self.released=0;self.notifications=[];self.parent=True;self.war=False;self.ai=False;self.jobs=[];self.deficit=False;self.draw=99;self.enabled=[]
 def condition(self,nodes):
  out=[]
  for key,op,value in nodes:
   if key=='NOT':answer=not self.condition(value)
   elif key=='OR':answer=any(self.condition([n]) for n in value)
   elif key=='AND':answer=self.condition(value)
   elif key=='check_variable':
    a=fields(value);operator=next(o for k,o,v in value if k=='value');x=self.variables.get(a['which'],0);y=float(a['value'])
    answer={'>':x>y,'<':x<y,'>=':x>=y,'<=':x<=y,'=':x==y}[operator]
   elif key=='has_country_flag':answer=value in self.flags
   elif key=='is_ai':answer=self.ai==(value=='yes')
   elif key=='is_at_war':answer=self.war==(value=='yes')
   elif key=='has_resource':
    a=fields(value);operator=next(o for k,o,v in value if k=='amount');x=self.resources.get(a['type'],0);y=float(a['amount'])
    answer={'>':x>y,'<':x<y,'>=':x>=y,'<=':x<=y,'=':x==y}[operator]
   elif key=='has_deficit':answer=self.deficit
   elif key=='haipam_is_empire':answer=self.parent
   elif key in salvation_triggers:answer=self.condition(salvation_triggers[key])
   elif key=='haipam_is_frontier_parent':answer=self.parent
   elif key=='haipam_frontier_can_advance':answer=self.parent and not self.war and not self.temple and 'haipam_frontier_paused' not in self.flags
   elif key=='any_owned_planet':answer=self.temple if 'has_active_building' in fields(value) else self.colony
   else:raise AssertionError('Unsupported frontier test predicate '+key)
   out.append(answer)
  return all(out)
 def execute(self,nodes):
  previous_if=False
  for key,op,value in nodes:
   if key=='if':
    previous_if=self.condition(fields(value)['limit'])
    if previous_if:self.execute([n for n in value if n[0]!='limit'])
   elif key=='else':
    if not previous_if:self.execute(value)
   elif key=='set_variable':a=fields(value);self.variables[a['which']]=float(a['value'])
   elif key=='change_variable':a=fields(value);self.variables[a['which']]=self.variables.get(a['which'],0)+float(a['value'])
   elif key=='set_country_flag':self.flags.add(value)
   elif key=='remove_country_flag':self.flags.discard(value)
   elif key=='set_timed_country_flag':self.flags.add(fields(value)['flag'])
   elif key=='add_resource':
    for k,o,v in value:self.resources[k]+=float(v)
   elif key=='country_event':self.notifications.append(fields(value)['id'])
   elif key=='planet_event':self.jobs.append(fields(value))
   elif key=='enable_faction_of_type':self.enabled.append(value)
   elif key=='random_list':
    mark=0
    for weight,o,branch in value:
     mark+=int(weight)
     if self.draw<mark:self.execute(branch);break
   elif key=='root':self.execute(value)
   elif key=='random_system':
    text=str(fields(value)['limit'])
    if (self.station if 'haipam_frontier_system_candidate' in text else self.colony):self.execute([n for n in value if n[0]!='limit'])
   elif key=='random_system_planet':self.execute([n for n in value if n[0]!='limit'])
   elif key=='haipam_release_frontier_colony':
    # Country creation/ownership aren't emulated; execute the real parent's
    # post-release accounting, independently checked against eligibility guards.
    self.released+=1
    self.execute([n for n in fields(effects[key])['if'] if n[0] in ['change_variable','set_variable','set_timed_country_flag']])
   elif key in effects:self.execute(effects[key])
   elif key in ['save_event_target_as','owner_species','set_planet_flag','set_star_flag','create_starbase','log']:pass
   else:raise AssertionError('Unsupported frontier test effect '+key)

def validate():
 cases=0
 # No eligible world, insufficient money, and fully eligible fixtures must have
 # different charges. Execute the actual effects rather than a copied formula.
 for station,colony,affordable in product([False,True],repeat=3):
  f=Fixture(station,colony);f.execute(effects['haipam_initialize_frontier'])
  if not affordable:f.resources={k:0 for k in f.resources}
  old=f.resources.copy();f.execute(effects['haipam_frontier_claim_one_system']);f.execute(effects['haipam_frontier_launch_one_colony'])
  assert old['alloys']-f.resources['alloys']==(100*station+200*colony if affordable else 0)
  assert old['influence']-f.resources['influence']==(50 if station and affordable else 0)
  assert len(f.jobs)==int(colony and affordable)
  if f.jobs:assert f.jobs[0]['days']=='360'
  cases+=1
 for paused,temple,war in product([False,True],repeat=3):
  f=Fixture(temple=temple);f.war=war
  f.execute(effects['haipam_initialize_frontier'])
  if paused:f.flags.add('haipam_frontier_paused')
  old=f.resources.copy();f.execute(events['haipam.300']['immediate'])
  blocked=paused or temple or war
  assert bool(f.jobs)==(not blocked)
  if blocked:assert f.resources==old
  cases+=1
 f=Fixture();f.execute(effects['haipam_initialize_frontier']);f.variables['hp_frontier_organization']=41
 f.execute(effects['haipam_initialize_frontier']);assert f.variables['hp_frontier_organization']==41
 cases+=1
 # Low organization requires two consecutive active years; cooldown and cap
 # prevent endless scripted fragmentation even under sustained expansion.
 for cooldown,at_cap in product([False,True],repeat=2):
  f=Fixture();f.execute(effects['haipam_initialize_frontier']);f.variables['hp_frontier_organization']=19
  if cooldown:f.flags.add('haipam_frontier_split_cooldown')
  if at_cap:f.variables['hp_frontier_children']=3
  f.execute(events['haipam.300']['immediate']);assert f.released==0
  f.execute(events['haipam.300']['immediate']);assert f.released==int(not cooldown and not at_cap)
  cases+=1
 f=Fixture();f.execute(effects['haipam_initialize_frontier']);f.variables['hp_frontier_organization']=12;f.variables['hp_frontier_low_years']=1
 f.temple=True;f.execute(events['haipam.300']['immediate']);assert f.variables['hp_frontier_low_years']==0 and f.released==0
 cases+=1
 # Inspect revalidation and ownership protection at the actual delayed landing.
 landing=str(events['haipam.321']['immediate'])
 for guard in ['haipam_frontier_owner','haipam_frontier_species','is_under_colonization','exists','has_anomaly','is_same_value','is_hostile']:assert guard in landing
 triggers=(MOD/'common/scripted_triggers/haipam_frontier_triggers.txt').read_text()
 assert 'is_capital = no' in triggers and 'haipam_homeworld' in triggers and 'count = 1' in triggers
 # The two story branches cannot schedule one another. Aid is a transfer, not
 # a free grant; rise selects the native synthetic path in the NPC only.
 steel={fields(v)['id']:fields(v) for k,o,v in parse((MOD/'events/haipam_steel_events.txt').read_text()) if k!='namespace'}
 request=next(v for k,o,v in parse((MOD/'events/haipam_steel_events.txt').read_text()) if isinstance(v,list) and fields(v).get('id')=='haipam.401')
 options=[v for k,o,v in request if k=='option']
 aid,refuse=map(fields,options)
 assert fields(aid['add_resource'])['food']=='-3000'
 assert 'haipam.405' in str(aid) and 'haipam.402' not in str(aid)
 assert 'haipam.402' in str(refuse) and 'haipam.405' not in str(refuse)
 steel_effects=(MOD/'common/scripted_effects/haipam_steel_effects.txt').read_text()
 assert 'add_ascension_perk = ap_synthetic_evolution' in steel_effects and 'add_tradition = tr_synthetics_adopt' in steel_effects
 assert 'trait_haipam_gray' not in steel_effects and 'change_species' not in steel_effects
 assert 'has_truce' in str(steel['haipam.406'])
 assert 'is_at_war_with' in str(steel['haipam.406'])
 faction_events={fields(v)['id']:fields(v) for k,o,v in parse((MOD/'events/haipam_salvation_events.txt').read_text()) if k!='namespace'}
 monthly=faction_events['haipam.620']['immediate'];faction_cases=0;unlocked=0
 for roll in range(100):
  f=Fixture();f.draw=roll
  f.execute(monthly);assert not f.enabled
  f.execute(faction_events['haipam.622']['immediate']);f.execute(monthly)
  unlocked+=int('haipam_salvation_unlocked' in f.flags);faction_cases+=1
 assert unlocked==10
 f=Fixture();f.resources['food']=100
 for i in range(2):f.execute(monthly);assert not f.enabled
 f.execute(monthly);assert 'haipam_salvation_unlocked' in f.flags
 f.resources['food']=1000;f.execute(monthly);assert f.variables['hp_salvation_hunger_months']==0
 faction_cases+=1
 f=Fixture();f.deficit=True;f.resources['food']=10000
 for i in range(3):f.execute(monthly)
 assert 'haipam_salvation_unlocked' in f.flags;faction_cases+=1
 resource=fields(parse((MOD/'common/static_modifiers/haipam_resource_cradle.txt').read_text()))['haipam_resource_cradle']
 assert fields(resource)['planet_jobs_minerals_produces_mult']=='1.0'
 for _,_,body in parse((MOD/'common/deposits/haipam_homeworld_deposits.txt').read_text()):
  assert fields(body)['planet_modifier']==[], 'Resource bonuses double-counted in deposits and visible modifier'
 report={'ok':True,'frontier_control_flow_cases':cases,'story_branches_checked':2,'salvation_faction_cases':faction_cases,'resource_modifier_double_count_guard':True,'engine_scopes_verified':False,'gameplay_verified':False}
 print(json.dumps(report));return report
if __name__=='__main__':validate()
