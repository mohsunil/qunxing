"""Haipam's resource-rich motherworld; all balance figures are prototypes.

Adds developable deposits and productive jobs, not monthly resource injections.
The monthly repair is bounded to the original flagged motherworld.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'mod/haipam'
def put(path,text):
    p=MOD/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

features=[
 ('deep_mantle','d_ore_rich_caverns','deposit_cat_minerals'),
 ('energy_network','d_geothermal_vent','deposit_cat_energy'),
 ('nutrient_seas','d_fertile_lands','deposit_cat_food'),
 ('rare_strata','d_crystalline_caverns','deposit_cat_rare_resource'),
]
deposits=[]
for key,icon,category in features:
    rare=''
    if key=='rare_strata':
        for tech,stat in [('tech_mine_rare_crystals','planet_miners_rare_crystals_produces_add'),
                          ('tech_mine_exotic_gases','planet_farmers_exotic_gases_produces_add'),
                          ('tech_mine_volatile_motes','planet_technician_volatile_motes_produces_add')]:
            rare+=f'''triggered_planet_modifier = {{
 potential = {{ exists = owner owner = {{ has_technology = {tech} }} }}
 modifier = {{ {stat} = 0.05 }}
}}\n'''
    deposits.append(f'''d_haipam_{key} = {{
 icon = {icon} is_for_colonizable = yes category = {category}
 use_for_min_max_adjustments = yes should_swap_deposit_on_terraforming = no
 can_be_cleared = {{ always = no }}
 potential = {{ has_planet_flag = haipam_homeworld }}
 drop_weight = {{ weight = 0 }}
 planet_modifier = {{ }}
 {rare}
}}''')
put('common/deposits/haipam_homeworld_deposits.txt','\n\n'.join(deposits))
put('common/static_modifiers/haipam_resource_cradle.txt', '''haipam_resource_cradle = {
 icon = "gfx/interface/icons/haipam/civic_haipam_royal_biology.dds" icon_frame = 1
 planet_max_districts_add = 12
 district_mining_max_add = 12 district_generator_max_add = 10 district_farming_max_add = 10
 planet_jobs_minerals_produces_mult = 1.0
 planet_jobs_energy_produces_mult = 0.75 planet_jobs_food_produces_mult = 0.75
}''')
effect='''# Colony scope. Never enroll a new capital or another colony as the motherworld.
haipam_enrich_homeworld = {
 if = {
  limit = { exists = owner owner = { haipam_is_empire = yes }
   planet = { has_planet_flag = haipam_homeworld } }
'''
for key,*_ in features:
    effect+=f'''  if = {{ limit = {{ NOT = {{ has_deposit = d_haipam_{key} }} }}
   add_deposit = d_haipam_{key} }}
'''
effect+='''  if = { limit = { NOT = { has_modifier = haipam_resource_cradle } }
   add_modifier = { modifier = haipam_resource_cradle days = -1 } }
  set_planet_flag = haipam_resource_cradle_v1
 }
}'''
put('common/scripted_effects/haipam_homeworld.txt',effect)
put('events/haipam_homeworld_events.txt','''namespace = haipam
country_event = {
 id = haipam.260 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes has_country_flag = haipam_home_registered }
 immediate = {
  every_owned_planet = {
   limit = { planet = { has_planet_flag = haipam_homeworld } }
   haipam_enrich_homeworld = yes
  }
 }
}''')
put('common/on_actions/haipam_homeworld_on_actions.txt',
    'on_monthly_pulse_country = { events = { haipam.260 } }')
p=MOD/'events/haipam_population_events.txt';s=p.read_text(encoding='utf-8')
old='   add_deposit = d_geothermal_vent\n   add_deposit = d_ore_rich_caverns\n   add_deposit = d_fertile_lands'
s=s.replace(old,'   haipam_enrich_homeworld = yes')
p.write_text(s,encoding='utf-8')
loc={
 'haipam_resource_cradle':'海帕姆：资源母星',
 'haipam_resource_cradle_desc':'母星拥有深层矿床、地热能源网络、营养海与稀有元素共生层。资源需要通过区划、岗位和开采科技利用。',
 'd_haipam_deep_mantle':'海帕姆·深层富矿',
 'd_haipam_deep_mantle_desc':'母星的深层矿床与可开发陆架。采矿区域上限+12，行星总区域上限+12，矿物岗位产出+100%。',
 'd_haipam_energy_network':'海帕姆·行星能源脉络',
 'd_haipam_energy_network_desc':'密集的地热与能源沉积网络。发电区域上限+10，能量岗位产出+75%。',
 'd_haipam_nutrient_seas':'海帕姆·原生营养海',
 'd_haipam_nutrient_seas_desc':'富含有机养分的海洋和沿岸生态。农业区域上限+10，食物岗位产出+75%。',
 'd_haipam_rare_strata':'海帕姆·稀有元素共生层',
 'd_haipam_rare_strata_desc':'研究对应开采科技后，矿工附带产出稀有水晶，农业岗位附带产出异星天然气，技工附带产出易爆微粒。必须有实际就业人口才能开采。',
}
for language in ['english','simp_chinese']:
    (MOD/f'localisation/{language}/haipam_homeworld_l_{language}.yml').write_text(
        'l_'+language+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'homeworld_features':4,'old_save_repair':'next monthly pulse on original motherworld',
 'resource_injections':False,'balance':'prototype','gameplay_verified':False}))
