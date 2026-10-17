"""Original Haipam navy definitions; native art is referenced, never copied.

All numeric balance values are prototypes and require actual combat testing.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT/'mod/haipam'
def put(path, text):
    dest=MOD/path;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(text.strip()+'\n',encoding='utf-8')

sizes=[('light','corvette',1000,0.5,1,180,45,0.05,'small',300),
       ('medium','destroyer',4000,1,1,140,90,0.12,'medium',600),
       ('heavy','cruiser',12000,2,2,110,180,0.30,'heavy',1200)]
definitions=[];utilities=[]
for tier,proxy,hp,capacity,fleet_slot,speed,time,upkeep,tech,power in sizes:
    slots={'light':'"mid" = { locator = "part1" }',
           'medium':'"bow" = { locator = "part1" } "stern" = { locator = "part2" }',
           'heavy':'"bow" = { locator = "part1" } "mid" = { locator = "part2" } "stern" = { locator = "part3" }'}[tier]
    definitions.append(f'''haipam_axial_{tier} = {{
 entity = "haipam_{tier}_entity" use_shipnames_from = {proxy}
 formation_priority = 20 max_speed = {speed} acceleration = 0.30 rotation_speed = 0.08
 collision_radius = 6 max_hitpoints = {hp}
 size_multiplier = {capacity} fleet_slot_size = {fleet_slot}
 map_counter_icon = ship_counter_4 icon = ship_size_military_1
 section_slots = {{ {slots} }} num_target_locators = 2
 is_space_station = no base_buildtime = {time}
 enable_default_design = yes enable_3dview_in_ship_browser = yes
 default_behavior = artillery ship_roles = {{ artillery gunship }}
 prerequisites = {{ "tech_haipam_fleetization" "tech_haipam_axial_{tech}" "tech_{proxy}s" }}
 potential_country = {{ OR = {{ haipam_is_empire = yes has_country_flag = haipam_steel_origin }} }}
 class = shipclass_military construction_type = starbase_shipyard
 required_component_set = "power_core" required_component_set = "ftl_components"
 required_component_set = "thruster_components" required_component_set = "sensor_components"
 required_component_set = "combat_computers"
 modifier = {{ ship_shield_mult = -0.98 ship_evasion_add = 0.10 }}
 combat_disengage_chance = 1.0
 resources = {{ category = ships upkeep = {{ energy = 0.01 alloys = {upkeep} }} }}
 min_upgrade_cost = {{ alloys = 1 }}
 ai_ship_data = {{ fraction = {{ base = 30 }} }}
}}''')
    utilities.append(f'''utility_component_template = {{
 key = "HAIPAM_{tier.upper()}_REACTOR" size = small
 icon = "GFX_ship_part_reactor_3" power = {power}
 component_set = "power_core"
 potential = {{ is_ship_size = haipam_axial_{tier} }}
 resources = {{ category = ship_components cost = {{ alloys = {power//15} }} }}
 ai_weight = {{ weight = 100 }}
}}''')
put('common/ship_sizes/haipam_ship_sizes.txt','\n\n'.join(definitions))

selection='OR = { '+' '.join('is_ship_size = haipam_axial_'+t[0] for t in sizes)+' }'
utilities.append(f'''utility_component_template = {{
 key = "HAIPAM_THRUSTER" size = small icon = "GFX_ship_part_thruster_2" power = -10
 component_set = "thruster_components"
 potential = {{ {selection} }}
 modifier = {{ ship_speed_mult = 0.25 }}
 resources = {{ category = ship_components cost = {{ alloys = 10 }} }}
 ai_weight = {{ weight = 100 }}
}}
utility_component_template = {{
 key = "HAIPAM_COMBAT_COMPUTER" size = small icon = "GFX_ship_part_computer_default" power = -5
 component_set = "combat_computers" ship_behavior = artillery
 potential = {{ {selection} }}
 modifier = {{ ship_fire_rate_mult = 0.15 }}
 resources = {{ category = ship_components cost = {{ alloys = 10 }} }}
 ai_weight = {{ weight = 100 }}
}}''')
put('common/component_templates/haipam_utilities.txt','\n\n'.join(utilities))

# Damage uses the documented 4.5.2 script form, not nonexistent min_damage keys.
weapons=[]
for size,tech,low,high,cost,power,range_,tracking in [
 ('small','small',30,55,40,-12,50,0.60),
 ('medium','medium',80,130,90,-30,75,0.30),
 ('large','heavy',200,350,180,-70,110,0.10)]:
    weapons.append(f'''weapon_component_template = {{
 key = "HAIPAM_{size.upper()}_AXIAL_PLASMA" size = {size} type = instant
 icon = "GFX_haipam_axial_plasma" icon_frame = 1
 component_set = "HAIPAM_AXIAL_PLASMA" projectile_gfx = "plasma_thrower_{size[0]}"
 prerequisites = {{ "tech_haipam_axial_{tech}" }}
 potential = {{ from = {{ OR = {{ haipam_is_empire = yes has_country_flag = haipam_steel_origin }} }} }}
 damage = {{ min = {low} max = {high} }} power = {power}
 range = {range_} accuracy = 0.90 tracking = {tracking}
 hull_damage = 1.75 armor_damage = 2.0 shield_damage = 0.50
 tags = {{ weapon_type_energy {size[0]}_slot }}
 ai_tags = {{ weapon_role_anti_armor artillery gunship }}
 resources = {{ category = ship_components cost = {{ alloys = {cost} }} }}
 ai_weight = {{ weight = 100 }}
}}''')
put('common/component_templates/haipam_axial_weapons.txt','\n\n'.join(weapons))
put('common/component_sets/haipam_component_sets.txt', '''component_set = {
 key = "HAIPAM_AXIAL_PLASMA" icon = "GFX_haipam_axial_plasma" icon_frame = 1
}''')

sections=[
 ('LIGHT_CORE','light','mid','haipam_light_core_entity',[('small',1),('small',2),('small',3)],4,160),
 ('MEDIUM_BOW','medium','bow','haipam_medium_bow_entity',[('medium',1),('small',1),('small',2)],6,240),
 ('MEDIUM_STERN','medium','stern','haipam_medium_stern_entity',[('small',1),('small',2)],2,100),
 ('HEAVY_BOW','heavy','bow','haipam_heavy_bow_entity',[('large',1)],4,300),
 ('HEAVY_CORE','heavy','mid','haipam_heavy_core_entity',[('medium',1),('medium',2),('medium',3)],6,400),
 ('HEAVY_STERN','heavy','stern','haipam_heavy_stern_entity',[('medium',1)],2,150),
]
parts=[]
for key,tier,slot,entity,guns,utility,cost in sections:
    comps='\n'.join(f'component_slot = {{ name = "{s.upper()}_GUN_{n:02d}" template = "{s}_turret" locatorname = "{s}_gun_{n:02d}" }}' for s,n in guns)
    parts.append(f'''ship_section_template = {{
 key = "HAIPAM_{key}" ship_size = haipam_axial_{tier} fits_on_slot = {slot}
 should_draw_components = no entity = "{entity}" icon = "GFX_ship_part_core_{slot}"
 {comps}
 small_utility_slots = {utility} aux_utility_slots = 1
 resources = {{ category = ship_sections cost = {{ alloys = {cost} }} }}
 ai_tags = {{ artillery gunship }} ai_weight = {{ weight = 100 }}
}}''')
put('common/section_templates/haipam_sections.txt','\n\n'.join(parts))

put('common/global_ship_designs/haipam_designs.txt', '''ship_design = {
 name = "NAME_HAIPAM_POSTAL_RETURN" ship_size = haipam_axial_light
 is_event_design = yes hide_size = yes
 section = {
  template = "HAIPAM_LIGHT_CORE" slot = "mid"
  component = { slot = "SMALL_GUN_01" template = "HAIPAM_SMALL_AXIAL_PLASMA" }
  component = { slot = "SMALL_GUN_02" template = "HAIPAM_SMALL_AXIAL_PLASMA" }
  component = { slot = "SMALL_GUN_03" template = "HAIPAM_SMALL_AXIAL_PLASMA" }
  component = { slot = "SMALL_UTILITY_1" template = "SMALL_ARMOR_1" }
  component = { slot = "SMALL_UTILITY_2" template = "SMALL_ARMOR_1" }
  component = { slot = "SMALL_UTILITY_3" template = "SMALL_ARMOR_1" }
  component = { slot = "SMALL_UTILITY_4" template = "SMALL_ARMOR_1" }
 }
 required_component = "HAIPAM_LIGHT_REACTOR"
 required_component = "HAIPAM_THRUSTER"
 required_component = "HAIPAM_COMBAT_COMPUTER"
 required_component = "HYPER_DRIVE_1" required_component = "SENSOR_1"
}''')
put('events/haipam_postal_events.txt', '''namespace = haipam
country_event = {
 id = haipam.240 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes exists = capital_scope
  has_technology = tech_haipam_postal_fleets has_technology = tech_haipam_fleetization
  has_technology = tech_haipam_axial_small
  NOT = { has_country_flag = haipam_postal_offer_pending }
  any_owned_planet = { has_active_building = building_haipam_postal_hub } }
 immediate = { random_list = { 75 = { } 25 = {
  set_country_flag = haipam_postal_offer_pending country_event = { id = haipam.241 days = 10 }
 } } }
}
country_event = {
 id = haipam.241 is_triggered_only = yes title = haipam.241.name desc = haipam.241.desc
 picture = GFX_haipam_evt_postal
 option = {
  name = haipam.241.repair allow = { has_resource = { type = alloys amount >= 100 } exists = capital_scope }
  add_resource = { alloys = -100 } remove_country_flag = haipam_postal_offer_pending
  create_fleet = {
   name = "NAME_HAIPAM_POSTAL_FLEET"
   effect = {
    set_owner = root
    create_ship = { name = "NAME_HAIPAM_POSTAL_RETURN" design = "NAME_HAIPAM_POSTAL_RETURN" prefix = no upgradable = no }
    set_location = root.capital_scope
   }
  }
 }
 option = { name = haipam.241.scrap add_resource = { alloys = 50 }
  remove_country_flag = haipam_postal_offer_pending }
}''')
put('common/on_actions/haipam_navy_on_actions.txt','on_yearly_pulse_country = { events = { haipam.240 } }')
loc={
 'haipam_axial_light':'轻型轴炮舰','haipam_axial_medium':'中型轴炮舰','haipam_axial_heavy':'重型轴炮舰',
 'HAIPAM_AXIAL_PLASMA':'等离子轴炮','HAIPAM_SMALL_AXIAL_PLASMA':'小型等离子轴炮',
 'HAIPAM_MEDIUM_AXIAL_PLASMA':'中型等离子轴炮','HAIPAM_LARGE_AXIAL_PLASMA':'重型等离子轴炮',
 'HAIPAM_LIGHT_REACTOR':'轻舰轴炮反应堆','HAIPAM_MEDIUM_REACTOR':'中舰轴炮反应堆',
 'HAIPAM_HEAVY_REACTOR':'重舰轴炮反应堆','HAIPAM_THRUSTER':'舰团推进器','HAIPAM_COMBAT_COMPUTER':'轴炮协同火控',
 'NAME_HAIPAM_POSTAL_FLEET':'邮政回收舰队','NAME_HAIPAM_POSTAL_RETURN':'归邮者',
 'haipam.241.name':'旧船返航','haipam.241.desc':'邮政舰队在偏离主航线的补给点找到一艘旧式轴炮舰。船体仍可使用，需要合金完成维修。修复后它将照常占用海军容量并消耗维护资源。',
 'haipam.241.repair':'支付100合金，修复并接收。','haipam.241.scrap':'拆解回收50合金。',
}
for key,*_ in sections:loc['HAIPAM_'+key]='轴炮舰段：'+{'LIGHT_CORE':'轻舰核心','MEDIUM_BOW':'中舰舰艏','MEDIUM_STERN':'中舰舰艉','HEAVY_BOW':'重舰舰艏','HEAVY_CORE':'重舰核心','HEAVY_STERN':'重舰舰艉'}[key]
for tier,*_ in sizes:
    loc['haipam_axial_'+tier+'_plural']=loc['haipam_axial_'+tier]
for key in list(loc):
    if key.startswith('HAIPAM_'):loc[key+'_DESC']='海帕姆专用舰团设备。原型数值，待实战调校。'
for language in ['english','simp_chinese']:
    path=MOD/f'localisation/{language}/haipam_navy_l_{language}.yml'
    path.write_text('l_'+language+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'ship_sizes':3,'weapons':3,'sections':6,'required_components':5,'postal_return_event':True,'runtime_verified':False}))
