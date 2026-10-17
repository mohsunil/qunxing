"""Motherworld orbital arsenal. Habitat and population are preserved.

Native construction/shipyard entities are temporary presentation references.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/haipam'
def put(path,text):
 p=MOD/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

stages=[]
for stage,time,alloys,unity,capacity,speed in [(0,720,3000,1000,0,0),(1,1440,8000,2000,10,0.5),(2,1800,16000,3000,25,1.0),(3,2160,30000,5000,60,2.0)]:
 entity='construction_platform_entity' if stage==0 else f'mega_shipyard_01_stage_{stage}_entity'
 previous='' if stage==0 else f'upgrade_from = {{ haipam_arsenal_{stage-1} }}'
 site='''possible = {
  exists = starbase is_inside_border = from
  from = { NOT = { has_country_flag = haipam_arsenal_built } }
 }
 placement_rules = { planet_possible = {
  has_planet_flag = haipam_homeworld is_colony = yes exists = owner
  owner = { is_same_value = prev.from }
  NOT = { has_anomaly = yes }
  NOT = { has_planet_flag = has_megastructure }
 } }
 on_build_complete = {
  from = { set_country_flag = haipam_arsenal_built country_event = { id = haipam.251 days = 1 } }
 }''' if stage==0 else f'''station_modifier = {{ starbase_shipyard_capacity_add = {capacity} }}
 country_modifier = {{ starbase_shipyard_build_speed_mult = {speed} }}
 on_build_complete = {{ from = {{ country_event = {{ id = haipam.{251+stage} days = 1 }} }} }}'''
 stages.append(f'''haipam_arsenal_{stage} = {{
 entity = "{entity}" construction_entity = "{entity}"
 portrait = GFX_haipam_evt_arsenal place_entity_on_planet_plane = no
 entity_offset = {{ x = -18 y = -18 }} build_time = {time}
 prerequisites = {{ "tech_haipam_planetary_arsenal" }}
 potential = {{ haipam_is_empire = yes has_technology = tech_haipam_planetary_arsenal }}
 resources = {{ category = megastructures cost = {{ alloys = {alloys} unity = {unity} }} upkeep = {{ energy = {5+stage*10} }} }}
 {previous}
 {site}
 ai_weight = {{ factor = 10 }}
}}''')
put('common/megastructures/haipam_arsenal.txt','\n\n'.join(stages))
put('common/on_actions/haipam_arsenal_on_actions.txt','on_monthly_pulse_country = { events = { haipam.250 } }')
events=['''namespace = haipam
country_event = {
 id = haipam.250 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes exists = capital_scope NOT = { has_country_flag = haipam_home_registered } }
 immediate = {
  capital_scope = { planet = { set_planet_flag = haipam_homeworld } }
  set_country_flag = haipam_home_registered
 }
}''']
for stage in range(4):
 eid=251+stage
 events.append(f'''country_event = {{
 id = haipam.{eid} is_triggered_only = yes title = haipam.{eid}.name desc = haipam.{eid}.desc
 picture = GFX_haipam_evt_arsenal option = {{ name = haipam.arsenal.ok }}
}}''')
put('events/haipam_arsenal_events.txt','\n\n'.join(events))
# Initial registration happens before the first monthly pulse; migrating alpha
# saves register the current capital only once, and never silently move the site.
p=MOD/'events/haipam_population_events.txt';s=p.read_text(encoding='utf-8')
marker='  set_country_flag = haipam_initialized'
if 'set_country_flag = haipam_home_registered' not in s:
 s=s.replace(marker,marker+'\n  capital_scope = { planet = { set_planet_flag = haipam_homeworld } }\n  set_country_flag = haipam_home_registered',1)
 p.write_text(s,encoding='utf-8')
loc={
 'haipam_arsenal_0':'海帕姆舰造基址','haipam_arsenal_1':'海帕姆轨道装配厂',
 'haipam_arsenal_2':'海帕姆行星船坞群','haipam_arsenal_3':'海帕姆皇家舰造世界',
 'haipam_arsenal_0_DESC':'在海帕姆母星轨道建立分阶段舰造工程。母星居民、地表与已有建筑保留。',
 'haipam_arsenal_1_DESC':'十条舰造线投入运转；提高全帝国造舰速度。',
 'haipam_arsenal_2_DESC':'扩建为二十五条舰造线，进一步提升补舰能力。',
 'haipam_arsenal_3_DESC':'六十条舰造线形成环绕母星的工业体系；全帝国造舰速度提高200%。原型数值，待性能和实战验证。',
 'haipam.251.name':'舰造基址建成','haipam.251.desc':'海帕姆星的轨道基址已完成固定与补给接口。下一阶段将安装第一批船坞。',
 'haipam.252.name':'轨道装配厂投产','haipam.252.desc':'十条生产线已就绪。船体、装甲与轴炮部件可以在同一工业链中装配。',
 'haipam.253.name':'行星船坞群','haipam.253.desc':'轨道生产能力扩大到二十五条舰造线，母星供应体系开始支撑大规模舰团补充。',
 'haipam.254.name':'皇家舰造世界','haipam.254.desc':'六十条舰造线在海帕姆星轨道运行。母星仍是可居住的帝国中心，轨道设施则承接舰团的批量生产。',
 'haipam.arsenal.ok':'让下一批舰船进入装配。',
}
for language in ['english','simp_chinese']:
 (MOD/f'localisation/{language}/haipam_arsenal_l_{language}.yml').write_text('l_'+language+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'arsenal_stages':4,'homeworld_preserved':True,'native_3d_placeholder':True,'runtime_verified':False}))
