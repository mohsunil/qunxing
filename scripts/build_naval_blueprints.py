"""Three researched production blueprints; no free ships or player resources."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'mod/haipam'
specs=[
 ('LIGHT','small','corvettes',[
  ('HAIPAM_LIGHT_CORE','mid',[('SMALL_GUN_0'+str(i),'SMALL') for i in range(1,4)],4)]),
 ('MEDIUM','medium','destroyers',[
  ('HAIPAM_MEDIUM_BOW','bow',[('MEDIUM_GUN_01','MEDIUM'),('SMALL_GUN_01','SMALL'),('SMALL_GUN_02','SMALL')],6),
  ('HAIPAM_MEDIUM_STERN','stern',[('SMALL_GUN_01','SMALL'),('SMALL_GUN_02','SMALL')],2)]),
 ('HEAVY','heavy','cruisers',[
  ('HAIPAM_HEAVY_BOW','bow',[('LARGE_GUN_01','LARGE')],4),
  ('HAIPAM_HEAVY_CORE','mid',[(f'MEDIUM_GUN_0{i}','MEDIUM') for i in range(1,4)],6),
  ('HAIPAM_HEAVY_STERN','stern',[('MEDIUM_GUN_01','MEDIUM')],2)]),
]
designs=[];branches=[]
for tier,tech,hull,sections in specs:
 name='NAME_HAIPAM_PRODUCTION_'+tier
 d=f'ship_design = {{\n name = "{name}" ship_size = haipam_axial_{tier.lower()}\n is_event_design = yes\n'
 for key,slot,guns,armor in sections:
  d+=f' section = {{ template = "{key}" slot = "{slot}"\n'
  for socket,size in guns:d+=f'  component = {{ slot = "{socket}" template = "HAIPAM_{size}_AXIAL_PLASMA" }}\n'
  for i in range(1,armor+1):d+=f'  component = {{ slot = "SMALL_UTILITY_{i}" template = "SMALL_ARMOR_1" }}\n'
  d+=' }\n'
 for key in ['HAIPAM_'+tier+'_REACTOR','HAIPAM_THRUSTER','HAIPAM_COMBAT_COMPUTER','HYPER_DRIVE_1','SENSOR_1']:
  d+=f' required_component = "{key}"\n'
 designs.append(d+'}\n')
 branches.append(f'''if = {{ limit = {{ has_technology = tech_haipam_axial_{tech} has_technology = tech_{hull}
   NOT = {{ has_country_flag = haipam_blueprint_{tier.lower()} }} }}
  create_ship_design = {{ design = "{name}" }} add_ship_design = last_created_design
  set_country_flag = haipam_blueprint_{tier.lower()}
 }}''')
(MOD/'common/global_ship_designs/haipam_production_designs.txt').write_text('\n'.join(designs),encoding='utf-8')
(MOD/'events/haipam_blueprint_events.txt').write_text('''namespace = haipam
country_event = {
 id = haipam.242 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes has_technology = tech_haipam_fleetization }
 immediate = {
 '''+'\n '.join(branches)+'\n }\n}\n',encoding='utf-8')
(MOD/'common/on_actions/haipam_blueprint_on_actions.txt').write_text('on_monthly_pulse_country = { events = { haipam.242 } }\n',encoding='utf-8')
loc={'NAME_HAIPAM_PRODUCTION_LIGHT':'捕网级轴炮护卫舰',
 'NAME_HAIPAM_PRODUCTION_MEDIUM':'舰团中型轴炮舰',
 'NAME_HAIPAM_PRODUCTION_HEAVY':'长枪级D型轴炮重舰'}
for lang in ['english','simp_chinese']:
 (MOD/f'localisation/{lang}/haipam_blueprints_l_{lang}.yml').write_text('l_'+lang+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'production_blueprints':3,'free_ships':0,'gameplay_verified':False}))
