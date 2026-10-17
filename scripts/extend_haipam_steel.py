"""Original midgame white+robot state and grain / steel coalition prototype.

NPC seed resources/fleets are proposed event difficulty, never player gifts.
Native synthetic tradition adoption starts the DLC-appropriate ascension project.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'mod/haipam'
def put(rel,text):
 p=MOD/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

put('common/solar_system_initializers/haipam_steel_initializer.txt',r'''
# Event-only fallback, never a randomly spawned extra starting empire.
haipam_steel_refuge = {
 name = "NAME_HAIPAM_REFUGE_SYSTEM" class = sc_g
 flags = { haipam_steel_refuge }
 planet = { class = star orbit_distance = 0 orbit_angle = 0 size = 25 }
 planet = {
  name = "NAME_HAIPAM_REFUGE_WORLD" class = pc_continental size = 24
  orbit_distance = 70 orbit_angle = 90
  init_effect = { set_planet_flag = haipam_steel_refuge_world }
 }
 planet = { class = pc_barren size = 16 orbit_distance = 35 orbit_angle = 220 }
}
''')
put('common/scripted_triggers/haipam_steel_triggers.txt',r'''
haipam_steel_spawn_world = {
 is_colonizable = yes is_colony = no is_under_colonization = no
 NOT = { exists = owner } NOT = { has_anomaly = yes }
 habitability = { who = root.owner_species value >= 0.60 }
 solar_system = {
  NOT = { exists = owner } NOT = { exists = starbase }
  any_neighbor_system = { exists = owner owner = { is_same_value = root } }
  NOT = { any_fleet_in_system = { exists = owner owner = { is_hostile = root } } }
  NOT = { any_system_planet = { is_colony = yes } }
 }
}
''')
put('common/scripted_effects/haipam_steel_effects.txt',r'''
haipam_spawn_grain_polity = {
 save_event_target_as = haipam_grain_parent
 owner_species = { save_event_target_as = haipam_steel_founder }
 random_system = {
  limit = { any_system_planet = { haipam_steel_spawn_world = yes } }
  random_system_planet = {
   limit = { haipam_steel_spawn_world = yes }
   save_event_target_as = haipam_steel_world
  }
 }
 # A crowded midgame must not silently suppress the whole story. Add a single
 # event-owned refuge system, without taking existing empires' planets.
 if = { limit = { NOT = { exists = event_target:haipam_steel_world } }
  capital_scope = { solar_system = {
   spawn_system = {
    min_distance >= 25 max_distance <= 35 initializer = haipam_steel_refuge
    hyperlane = yes is_discovered = yes
    effect = { random_system_planet = {
     limit = { has_planet_flag = haipam_steel_refuge_world }
     save_event_target_as = haipam_steel_world
    } }
   }
  } }
 }
 if = { limit = { exists = event_target:haipam_steel_world }
  set_country_flag = haipam_grain_chain_started
  create_country = {
   name = "NAME_HAIPAM_STEEL" type = default authority = auth_oligarchic
   species = event_target:haipam_steel_founder origin = origin_mechanists
   ethos = { ethic = ethic_fanatic_materialist ethic = ethic_militarist }
   civics = { civic = civic_distinguished_admiralty civic = civic_functional_architecture }
   flag = { icon = { category = "haipam" file = "haipam_royal_crest.dds" }
    background = { category = "backgrounds" file = "horizontal.dds" }
    colors = { "black" "off_white" "wave_blue" "null" } }
   ignore_initial_colony_error = yes
   effect = {
    save_event_target_as = haipam_grain_polity
    set_country_flag = haipam_steel_origin set_country_flag = haipam_steel_of_@root
    copy_techs_from = { target = root }
    set_graphical_culture = arthropoid_01
    give_technology = { tech = tech_robotic_workers message = no }
    give_technology = { tech = tech_droid_workers message = no }
    set_policy = { policy = robot_pop_policy option = robot_pops_allowed cooldown = yes }
    set_policy = { policy = artificial_intelligence_policy option = ai_full_rights cooldown = yes }
    add_resource = { minerals = 10000 energy = 10000 alloys = 3000 consumer_goods = 3000 food = 500 }
   }
  }
  create_species = {
   name = "NAME_HAIPAM_INDUSTRIAL_ROBOT" plural = "NAME_HAIPAM_INDUSTRIAL_ROBOT"
   class = ROBOT portrait = default_robot traits = { trait = trait_mechanical }
   effect = { save_event_target_as = haipam_steel_robot }
  }
  event_target:haipam_steel_world = {
   solar_system = { create_starbase = { size = starbase_starport owner = event_target:haipam_grain_polity module = shipyard } }
   create_colony = { owner = event_target:haipam_grain_polity }
   colony = {
    set_capital = yes
    if = { limit = { has_building = building_colony_shelter } remove_building = building_colony_shelter }
    if = { limit = { NOT = { has_building = building_capital } } add_building = building_capital }
    add_building = building_robot_assembly_plant add_building = building_research_lab_1
    add_district = district_generator add_district = district_generator
    add_district = district_mining add_district = district_mining
    add_district = district_city add_district = district_city
    add_zone = { district = district_city zone = zone_research_unity zone_slot = 1 }
    add_zone = { district = district_city zone = zone_industrial zone_slot = 2 }
    add_building = { building = building_factory_1 zone = zone_industrial }
    add_building = { building = building_foundry_1 zone = zone_industrial }
    create_pop_group = { species = event_target:haipam_steel_founder category = specialist size = 800 }
    create_pop_group = { species = event_target:haipam_steel_robot category = worker size = 3200 }
   }
  }
  event_target:haipam_grain_polity = {
   create_starting_leaders = yes establish_communications_no_message = root
   every_owned_species = { limit = { has_trait = trait_mechanical }
    set_citizenship_type = { country = prev type = citizenship_full } }
  }
  establish_communications_no_message = event_target:haipam_grain_polity
  country_event = { id = haipam.401 days = 30 }
  log = "HAIPAM_WHITE_ROBOT_GRAIN_POLITY_CREATED"
 }
}
haipam_steel_industrial_rise = {
 if = { limit = { NOT = { has_country_flag = haipam_steel_mobilized } }
  set_country_flag = haipam_steel_mobilized set_country_flag = haipam_steel_war_pending
  give_technology = { tech = tech_synthetic_workers message = no }
  give_technology = { tech = tech_synthetic_leaders message = no }
  give_technology = { tech = tech_haipam_fleetization message = no }
  give_technology = { tech = tech_haipam_axial_small message = no }
  give_technology = { tech = tech_haipam_axial_medium message = no }
  give_technology = { tech = tech_haipam_axial_heavy message = no }
  give_technology = { tech = tech_cruisers message = no }
  add_ascension_perk = ap_synthetic_evolution
  add_tradition = tr_synthetics_adopt
  # Native adoption starts Digitization or the Utopia project. Do not fake a
  # completed ascension or convert any gray species from the player's empire.
  add_modifier = { modifier = haipam_steel_mobilization days = 7200 }
  add_resource = { minerals = 20000 energy = 20000 alloys = 20000 consumer_goods = 5000 }
  random_owned_species = { limit = { has_trait = trait_mechanical }
   save_event_target_as = haipam_steel_robot }
  capital_scope = { if = { limit = { exists = event_target:haipam_steel_robot }
   create_pop_group = { species = event_target:haipam_steel_robot category = worker size = 4000 } } }
  haipam_create_steel_armada = yes
  event_target:haipam_grain_parent = {
   country_event = { id = haipam.404 days = 1 }
   every_country = {
    limit = { is_ai = yes is_subject = no is_at_war = no has_country_flag = haipam_child_of_@prev }
    add_opinion_modifier = { who = event_target:haipam_grain_polity modifier = haipam_steel_solidarity }
    set_country_flag = haipam_steel_ally_of_@prev
   }
  }
  set_timed_country_flag = { flag = haipam_steel_preparing_war days = 1800 }
  log = "HAIPAM_STEEL_INDUSTRIAL_RISE_NATIVE_SYNTHETIC_PATH_STARTED"
 }
}
''')
# Event ship designs use our own components/sections with referenced native armor.
design='ship_design = {\n name = "NAME_HAIPAM_STEEL_LINE" ship_size = haipam_axial_heavy\n is_event_design = yes hide_size = yes\n'
for template,slot,guns,utilities in [
 ('HAIPAM_HEAVY_BOW','bow',[('LARGE_GUN_01','HAIPAM_LARGE_AXIAL_PLASMA')],4),
 ('HAIPAM_HEAVY_CORE','mid',[(f'MEDIUM_GUN_0{i}','HAIPAM_MEDIUM_AXIAL_PLASMA') for i in range(1,4)],6),
 ('HAIPAM_HEAVY_STERN','stern',[('MEDIUM_GUN_01','HAIPAM_MEDIUM_AXIAL_PLASMA')],2)]:
 design+=f' section = {{ template = "{template}" slot = "{slot}"\n'
 for gun,weapon in guns:design+=f' component = {{ slot = "{gun}" template = "{weapon}" }}\n'
 for i in range(1,utilities+1):design+=f' component = {{ slot = "SMALL_UTILITY_{i}" template = "SMALL_ARMOR_3" }}\n'
 design+=' }\n'
for key in ['HAIPAM_HEAVY_REACTOR','HAIPAM_THRUSTER','HAIPAM_COMBAT_COMPUTER','HYPER_DRIVE_1','SENSOR_1']:
 design+=f' required_component = "{key}"\n'
put('common/global_ship_designs/haipam_steel_designs.txt',design+'}')
fleet='haipam_create_steel_armada = {\n'
for batch in range(4):
 fleet+=' create_fleet = { name = "NAME_HAIPAM_STEEL_FLEET" effect = { set_owner = root\n'
 for i in range(6):fleet+=' create_ship = { name = random design = "NAME_HAIPAM_STEEL_LINE" prefix = no upgradable = yes }\n'
 for i in range(6):fleet+=' create_ship = { name = random design = "NAME_HAIPAM_POSTAL_RETURN" prefix = no upgradable = yes }\n'
 fleet+=' set_location = root.capital_scope\n } }\n'
put('common/scripted_effects/haipam_steel_armada.txt',fleet+'}')
put('common/static_modifiers/haipam_steel_modifiers.txt',r'''
haipam_steel_mobilization = {
 planet_jobs_produces_mult = 1.0 starbase_shipyard_build_speed_mult = 2.0
 country_naval_cap_add = 200 ships_upkeep_mult = -0.50
}
haipam_grain_repaid = { country_trade_produces_mult = 0.25 }
''')
put('common/opinion_modifiers/haipam_steel_opinions.txt',r'''
haipam_grain_aid = { opinion = { base = 150 } decay = { base = 3 } min = 0 }
haipam_grain_refused = { opinion = { base = -200 } decay = { base = 2 } max = 0 }
haipam_steel_solidarity = { opinion = { base = 200 } decay = { base = 1 } min = 0 }
''')
put('events/haipam_steel_events.txt',r'''
namespace = haipam
country_event = {
 id = haipam.400 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_frontier_parent = yes is_ai = no is_at_war = no mid_game_years_passed > 0
  NOT = { has_country_flag = haipam_grain_chain_started } }
 immediate = { haipam_spawn_grain_polity = yes }
}
country_event = {
 id = haipam.401 is_triggered_only = yes title = haipam.401.name desc = haipam.401.desc
 picture = GFX_haipam_evt_postal trigger = { exists = event_target:haipam_grain_polity }
 option = { name = haipam.401.aid allow = { has_resource = { type = food amount >= 3000 } }
  add_resource = { food = -3000 }
  event_target:haipam_grain_polity = { add_resource = { food = 3000 }
   add_opinion_modifier = { who = root modifier = haipam_grain_aid } }
  set_country_flag = haipam_grain_aided country_event = { id = haipam.405 days = 1800 }
 }
 option = { name = haipam.401.refuse
  set_country_flag = haipam_grain_refused
  event_target:haipam_grain_polity = { add_opinion_modifier = { who = root modifier = haipam_grain_refused } }
  country_event = { id = haipam.402 days = 180 }
 }
}
country_event = {
 id = haipam.402 is_triggered_only = yes title = haipam.402.name desc = haipam.402.desc
 picture = GFX_haipam_evt_hatchery
 trigger = { exists = event_target:haipam_grain_polity has_country_flag = haipam_grain_refused }
 immediate = { event_target:haipam_grain_polity = { country_event = { id = haipam.403 days = 720 } } }
 option = { name = haipam.402.ok }
}
country_event = {
 id = haipam.403 hide_window = yes is_triggered_only = yes
 trigger = { has_country_flag = haipam_steel_origin exists = capital_scope exists = event_target:haipam_grain_parent }
 immediate = { haipam_steel_industrial_rise = yes }
}
country_event = {
 id = haipam.404 is_triggered_only = yes title = haipam.404.name desc = haipam.404.desc
 picture = GFX_haipam_evt_arsenal option = { name = haipam.404.ok }
}
country_event = {
 id = haipam.405 is_triggered_only = yes title = haipam.405.name desc = haipam.405.desc
 picture = GFX_haipam_evt_postal
 trigger = { exists = event_target:haipam_grain_polity has_country_flag = haipam_grain_aided }
 immediate = { add_modifier = { modifier = haipam_grain_repaid days = 3600 } add_resource = { unity = 2000 } }
 option = { name = haipam.405.ok }
}
country_event = {
 id = haipam.406 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_frontier_parent = yes has_country_flag = haipam_grain_refused is_at_war = no is_subject = no }
 immediate = {
  save_event_target_as = haipam_grain_parent
  random_country = {
   limit = { has_country_flag = haipam_steel_of_@root has_country_flag = haipam_steel_war_pending
    is_subject = no is_at_war = no exists = capital_scope
    NOT = { has_country_flag = haipam_steel_preparing_war } NOT = { has_truce = root } }
   save_event_target_as = haipam_grain_polity
   add_casus_belli = { type = cb_humiliation who = root days = 3600 }
   declare_war = { target = root attacker_war_goal = wg_humiliation }
   if = { limit = { is_at_war_with = root }
    remove_country_flag = haipam_steel_war_pending
    root = {
     every_country = {
      limit = { is_ai = yes is_subject = no is_at_war = no
       has_country_flag = haipam_steel_ally_of_@root NOT = { has_truce = root } }
      join_war = event_target:haipam_grain_polity
     }
     country_event = { id = haipam.407 days = 1 }
    }
   }
  }
 }
}
country_event = {
 id = haipam.407 is_triggered_only = yes title = haipam.407.name desc = haipam.407.desc
 picture = GFX_haipam_evt_postal option = { name = haipam.407.ok }
}
''')
put('common/on_actions/haipam_steel_on_actions.txt','on_yearly_pulse_country = { events = { haipam.400 haipam.406 } }')
loc={
 'NAME_HAIPAM_REFUGE_SYSTEM':'边疆避难地','NAME_HAIPAM_REFUGE_WORLD':'避难星',
 'NAME_HAIPAM_STEEL':'钢铁蚊人共同体','NAME_HAIPAM_INDUSTRIAL_ROBOT':'边疆工业机器人',
 'NAME_HAIPAM_STEEL_LINE':'钢铁轴炮舰','NAME_HAIPAM_STEEL_FLEET':'钢铁动员舰团',
 'haipam_steel_mobilization':'钢铁工业动员','haipam_grain_repaid':'边疆粮援贸易回报',
 'haipam_grain_aid':'雪中送粮','haipam_grain_refused':'被拒绝的粮援','haipam_steel_solidarity':'钢铁舰团互助',
 'haipam.401.name':'独立舰团的借粮请求',
 'haipam.401.desc':'[haipam_grain_polity.GetName]由白蚊人与大量工业机器人组成。他们的工业开拓取得进展，有机居民的补给却陷入危机，请求帝国提供3000食物。',
 'haipam.401.aid':'拨出3000食物。','haipam.401.refuse':'拒绝粮援。',
 'haipam.402.name':'饿殍遍地',
 'haipam.402.desc':'“街道上已经没人争吵了。机器人照常工作，粮仓却没有东西能交给活着的人。”\n\n独立舰团最后的录音没有寒暄。幸存的白蚊人把资源集中到自动化与合成生命研究，求援频道随后归于沉寂。',
 'haipam.402.ok':'记录这段讯息。',
 'haipam.404.name':'钢铁蚊人崛起',
 'haipam.404.desc':'[haipam_grain_polity.GetName]扩建了机器人劳动力，启动合成飞升工程，完成舰队工业动员。四支舰团已经出港，其他自主舰团收到了联合邀请。\n\n他们还需五年整备。停战期、正在进行的战争和附庸关系会延后自动宣战。',
 'haipam.404.ok':'准备应对舰团。',
 'haipam.405.name':'粮援之后','haipam.405.desc':'独立舰团度过了补给危机，回报十年贸易合作（贸易产出+25%）及2000凝聚力。',
 'haipam.405.ok':'继续合作。',
 'haipam.407.name':'钢铁舰团的战争',
 'haipam.407.desc':'[haipam_grain_polity.GetName]正式宣战。已加入钢铁互助的独立海帕姆舰团，在没有战争、附庸或停战约束时加入进攻方。战争目标为羞辱；母星不会被事件直接转移。',
 'haipam.407.ok':'舰团进入战备。',
}
for language in ['english','simp_chinese']:
 p=MOD/f'localisation/{language}/haipam_steel_l_{language}.yml'
 p.write_text('l_'+language+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'steel_chain':True,'initial_composition':'white_and_robots','native_synthetic_path_started':True,'gameplay_verified':False}))
