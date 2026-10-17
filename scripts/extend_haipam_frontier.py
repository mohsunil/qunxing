"""Original autonomous frontier and peaceful Haipam secession prototype.

All costs, thresholds, intervals and starting cohort sizes are balance proposals.
No proprietary game source is embedded. Targets are rechecked on completion.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'mod/haipam'
def put(rel,text):
 p=MOD/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

put('common/scripted_triggers/haipam_frontier_triggers.txt',r'''
# Country scope. Child AI states expand through ordinary game AI, preventing
# recursive scripted creation of countries and one free pipeline per child.
haipam_is_frontier_parent = {
 haipam_is_empire = yes has_technology = tech_haipam_fleetization
 NOT = { has_country_flag = haipam_frontier_child }
}
haipam_frontier_can_advance = {
 haipam_is_frontier_parent = yes is_at_war = no
 NOT = { has_country_flag = haipam_frontier_paused }
 NOT = { any_owned_planet = { has_active_building = building_haipam_graviton_temple } }
}
# Solar-system scope; root is the paying country. All planets must be surveyed.
haipam_frontier_system_candidate = {
 NOT = { exists = owner } NOT = { exists = starbase }
 any_neighbor_system = { exists = owner owner = { is_same_value = root } }
 NOT = { any_system_planet = { is_surveyed = { who = root status = no } } }
 NOT = { any_system_planet = { is_colony = yes } }
 NOT = { any_fleet_in_system = { exists = owner owner = { is_hostile = root } } }
}
# Physical planet scope; the colonist species is the actual founder species.
haipam_frontier_colony_candidate = {
 is_colonizable = yes is_colony = no is_under_colonization = no
 NOT = { exists = owner } NOT = { has_anomaly = yes }
 NOT = { has_planet_flag = haipam_colonization_pending }
 is_surveyed = { who = root status = yes }
 habitability = { who = root.owner_species value >= 0.60 }
 solar_system = {
  exists = owner owner = { is_same_value = root }
  NOT = { any_fleet_in_system = { exists = owner owner = { is_hostile = root } } }
 }
}
# Colony scope. Only a mature automatically settled frontier colony can leave.
haipam_frontier_secession_candidate = {
 exists = owner owner = { is_same_value = root }
 is_capital = no has_planet_flag = haipam_frontier_colony
 NOT = { has_planet_flag = haipam_frontier_young }
 planet = { NOT = { has_planet_flag = haipam_homeworld } }
 any_owned_pop_group = { pop_group_has_trait = trait_haipam_white }
 solar_system = {
  exists = owner owner = { is_same_value = root } exists = starbase
  count_system_planet_colony = { count = 1 }
 }
}
''')

put('common/scripted_effects/haipam_frontier_effects.txt',r'''
# Country scope. Idempotent initialization, including already-started saves.
haipam_initialize_frontier = {
 if = {
  limit = { NOT = { has_country_flag = haipam_frontier_initialized } }
  set_country_flag = haipam_frontier_initialized
  set_variable = { which = hp_frontier_organization value = 80 }
  set_variable = { which = hp_frontier_low_years value = 0 }
  set_variable = { which = hp_frontier_children value = 0 }
  set_variable = { which = hp_frontier_stations value = 0 }
  set_variable = { which = hp_frontier_colonies value = 0 }
  if = { limit = { is_ai = no } country_event = { id = haipam.301 days = 1 } }
 }
}
haipam_clamp_frontier_organization = {
 if = { limit = { check_variable = { which = hp_frontier_organization value > 100 } }
  set_variable = { which = hp_frontier_organization value = 100 } }
 if = { limit = { check_variable = { which = hp_frontier_organization value < 0 } }
  set_variable = { which = hp_frontier_organization value = 0 } }
}
haipam_frontier_claim_one_system = {
 if = { limit = { haipam_frontier_can_advance = yes
   has_resource = { type = alloys amount >= 100 }
   has_resource = { type = influence amount >= 50 }
   has_resource = { type = energy amount >= 100 } }
  random_system = {
   limit = { haipam_frontier_system_candidate = yes }
   # Pay only after finding an eligible system, never on a failed search.
   root = { add_resource = { alloys = -100 influence = -50 energy = -100 }
    change_variable = { which = hp_frontier_organization value = -4 }
    change_variable = { which = hp_frontier_stations value = 1 } }
   create_starbase = { size = starbase_outpost owner = root }
   set_star_flag = haipam_frontier_claim
   log = "HAIPAM_FRONTIER_STATION_CREATED"
  }
 }
}
haipam_frontier_launch_one_colony = {
 if = { limit = { haipam_frontier_can_advance = yes
   has_resource = { type = alloys amount >= 200 }
   has_resource = { type = minerals amount >= 800 }
   has_resource = { type = food amount >= 300 }
   has_resource = { type = consumer_goods amount >= 200 }
   has_resource = { type = energy amount >= 200 } }
  save_event_target_as = haipam_frontier_owner
  owner_species = { save_event_target_as = haipam_frontier_species }
  random_system = {
   limit = { exists = owner owner = { is_same_value = root } any_system_planet = { haipam_frontier_colony_candidate = yes } }
   random_system_planet = {
    limit = { haipam_frontier_colony_candidate = yes }
    set_planet_flag = haipam_colonization_pending
    root = { add_resource = { alloys = -200 minerals = -800 food = -300 consumer_goods = -200 energy = -200 }
     change_variable = { which = hp_frontier_organization value = -6 } }
    # This is a PHYSICAL uncolonized planet, not an every_owned_planet colony.
    planet_event = { id = haipam.321 days = 360 }
    log = "HAIPAM_FRONTIER_COLONY_LAUNCHED"
   }
  }
 }
}
haipam_release_frontier_colony = {
 if = { limit = { is_at_war = no
   any_owned_planet = { haipam_frontier_secession_candidate = yes } }
  save_event_target_as = haipam_frontier_parent
  owner_species = { save_event_target_as = haipam_frontier_founder }
  random_owned_planet = {
   limit = { haipam_frontier_secession_candidate = yes }
   save_event_target_as = haipam_secession_colony
  }
  create_country = {
   name = { key = "NAME_HAIPAM_FRONTIER" variable_string = "\\[haipam_secession_colony.GetName\\]" }
   type = default authority = auth_imperial species = event_target:haipam_frontier_founder
   origin = origin_syncretic_evolution
   ethos = { ethic = ethic_authoritarian ethic = ethic_militarist ethic = ethic_spiritualist }
   civics = { civic = civic_haipam_royal_biology civic = civic_distinguished_admiralty }
   flag = { icon = { category = "haipam" file = "haipam_royal_crest.dds" }
    background = { category = "backgrounds" file = "horizontal.dds" }
    colors = { "wave_blue" "off_white" "black" "null" } }
   ignore_initial_colony_error = yes
   effect = {
    save_event_target_as = haipam_frontier_child
    set_country_flag = haipam_frontier_child
    set_country_flag = haipam_child_of_@root
    # Avoid re-running the motherworld gifts/royal initializer in a child state.
    set_country_flag = haipam_initialized set_country_flag = haipam_home_registered
    copy_techs_from = { target = root }
    set_graphical_culture = arthropoid_01
   }
  }
  event_target:haipam_secession_colony = {
   # This system has exactly one colony; no unrelated colony is transferred.
   solar_system = { starbase = { set_owner = event_target:haipam_frontier_child } }
   set_owner = event_target:haipam_frontier_child set_capital = yes
   if = { limit = { has_building = building_colony_shelter }
    remove_building = building_colony_shelter add_building = building_capital }
  }
  event_target:haipam_frontier_child = {
   every_owned_species = {
    if = { limit = { has_trait = trait_haipam_gray }
     set_citizenship_type = { country = prev type = citizenship_limited } }
   }
   create_starting_leaders = yes haipam_refresh_role_portraits = yes
   establish_communications_no_message = root
   set_truce = { target = root type = liberation }
   add_opinion_modifier = { who = root modifier = haipam_friendly_autonomy }
  }
  establish_communications_no_message = event_target:haipam_frontier_child
  set_truce = { target = event_target:haipam_frontier_child type = liberation }
  add_opinion_modifier = { who = event_target:haipam_frontier_child modifier = haipam_friendly_autonomy }
  change_variable = { which = hp_frontier_children value = 1 }
  change_variable = { which = hp_frontier_organization value = 20 }
  set_variable = { which = hp_frontier_low_years value = 0 }
  set_timed_country_flag = { flag = haipam_frontier_split_cooldown days = 3600 }
  if = { limit = { is_ai = no } country_event = { id = haipam.331 days = 1 } }
  log = "HAIPAM_FRIENDLY_FRONTIER_SECESSION"
 }
}
''')

put('events/haipam_frontier_events.txt',r'''
namespace = haipam
country_event = {
 id = haipam.302 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_frontier_parent = yes }
 immediate = { haipam_initialize_frontier = yes }
}
country_event = {
 id = haipam.300 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_frontier_parent = yes }
 immediate = {
  haipam_initialize_frontier = yes
  change_variable = { which = hp_frontier_organization value = 5 }
  if = { limit = { any_owned_planet = { has_active_building = building_haipam_graviton_temple } }
   change_variable = { which = hp_frontier_organization value = 5 }
   set_variable = { which = hp_frontier_low_years value = 0 } }
  haipam_frontier_claim_one_system = yes
  haipam_frontier_launch_one_colony = yes
  haipam_clamp_frontier_organization = yes
  if = { limit = { haipam_frontier_can_advance = yes
    check_variable = { which = hp_frontier_organization value < 35 }
    NOT = { has_country_flag = haipam_frontier_warning } }
   set_country_flag = haipam_frontier_warning
   if = { limit = { is_ai = no } country_event = { id = haipam.330 days = 1 } } }
  if = { limit = { check_variable = { which = hp_frontier_organization value >= 40 } }
   remove_country_flag = haipam_frontier_warning }
  if = { limit = { haipam_frontier_can_advance = yes
    check_variable = { which = hp_frontier_organization value < 20 } }
   change_variable = { which = hp_frontier_low_years value = 1 } }
  else = { set_variable = { which = hp_frontier_low_years value = 0 } }
  if = { limit = { haipam_frontier_can_advance = yes
    check_variable = { which = hp_frontier_low_years value >= 2 }
    check_variable = { which = hp_frontier_children value < 3 }
    NOT = { has_country_flag = haipam_frontier_split_cooldown } }
   haipam_release_frontier_colony = yes }
 }
}
country_event = {
 id = haipam.301 is_triggered_only = yes title = haipam.301.name desc = haipam.301.desc
 picture = GFX_haipam_evt_postal
 option = { name = haipam.301.advance }
 option = { name = haipam.301.pause set_country_flag = haipam_frontier_paused }
}
country_event = {
 id = haipam.310 is_triggered_only = yes title = haipam.310.name desc = haipam.310.desc
 picture = GFX_haipam_evt_postal
 immediate = { haipam_initialize_frontier = yes }
 option = { name = haipam.310.resume
  trigger = { has_country_flag = haipam_frontier_paused }
  remove_country_flag = haipam_frontier_paused }
 option = { name = haipam.310.pause
  trigger = { NOT = { has_country_flag = haipam_frontier_paused } }
  set_country_flag = haipam_frontier_paused }
 option = { name = haipam.310.reorganize
  allow = { has_resource = { type = unity amount >= 500 } has_resource = { type = energy amount >= 500 }
   NOT = { has_country_flag = haipam_frontier_reorganized } }
  add_resource = { unity = -500 energy = -500 }
  change_variable = { which = hp_frontier_organization value = 25 }
  set_variable = { which = hp_frontier_low_years value = 0 }
  set_timed_country_flag = { flag = haipam_frontier_reorganized days = 1800 }
  haipam_clamp_frontier_organization = yes }
 option = { name = haipam.310.close }
}
planet_event = {
 id = haipam.321 hide_window = yes is_triggered_only = yes
 immediate = {
  remove_planet_flag = haipam_colonization_pending
  if = { limit = { exists = event_target:haipam_frontier_owner exists = event_target:haipam_frontier_species
    event_target:haipam_frontier_owner = { haipam_is_empire = yes }
    is_colonizable = yes is_colony = no is_under_colonization = no NOT = { exists = owner }
    NOT = { has_anomaly = yes }
    solar_system = { exists = owner owner = { is_same_value = event_target:haipam_frontier_owner }
     NOT = { any_fleet_in_system = { exists = owner owner = { is_hostile = event_target:haipam_frontier_owner } } } } }
   create_colony = { owner = event_target:haipam_frontier_owner }
   colony = {
    create_pop_group = { species = event_target:haipam_frontier_species category = worker size = 200 }
    if = { limit = { NOT = { has_building = building_colony_shelter } } add_building = building_colony_shelter }
    if = { limit = { NOT = { has_building = building_haipam_royal_hatchery } } add_building = building_haipam_royal_hatchery }
    if = { limit = { NOT = { has_building = building_haipam_reactor } } add_building = building_haipam_reactor }
    set_planet_flag = haipam_frontier_colony
    set_timed_planet_flag = { flag = haipam_frontier_young days = 1800 }
    haipam_reset_pipeline = yes
   }
   event_target:haipam_frontier_owner = {
    change_variable = { which = hp_frontier_colonies value = 1 }
    if = { limit = { is_ai = no } country_event = { id = haipam.322 days = 1 } }
   }
   log = "HAIPAM_FRONTIER_COLONY_COMPLETED"
  }
  else = { log = "HAIPAM_FRONTIER_COLONY_CANCELLED_TARGET_CHANGED" }
 }
}
country_event = {
 id = haipam.322 is_triggered_only = yes title = haipam.322.name desc = haipam.322.desc
 picture = GFX_haipam_evt_hatchery option = { name = haipam.322.ok }
}
country_event = {
 id = haipam.330 is_triggered_only = yes title = haipam.330.name desc = haipam.330.desc
 picture = GFX_haipam_evt_postal
 option = { name = haipam.330.manage country_event = { id = haipam.310 days = 1 } }
 option = { name = haipam.330.continue }
}
country_event = {
 id = haipam.331 is_triggered_only = yes title = haipam.331.name desc = haipam.331.desc
 picture = GFX_haipam_evt_postal option = { name = haipam.331.ok }
}
''')
put('common/decisions/haipam_frontier_decisions.txt',r'''
decision_haipam_frontier_command = {
 icon = decision_discourage_growth owned_planets_only = yes enactment_time = 0
 potential = { is_capital = yes exists = owner owner = { haipam_is_frontier_parent = yes } }
 effect = { owner = { country_event = { id = haipam.310 days = 1 } } }
 ai_weight = { weight = 0 }
}
''')
put('common/on_actions/haipam_frontier_on_actions.txt',r'''
on_monthly_pulse_country = { events = { haipam.302 } }
on_yearly_pulse_country = { events = { haipam.300 } }
''')
put('common/opinion_modifiers/haipam_diplomacy.txt',
    'haipam_friendly_autonomy = { opinion = { base = 100 } decay = { base = 2 } min = 0 }')
put('common/scripted_loc/haipam_frontier_loc.txt',r'''
defined_text = {
 name = GetHaipamFrontierOrganization
 text = { trigger = { check_variable = { which = hp_frontier_organization value >= 70 } }
  localization_key = haipam.org.high }
 text = { trigger = { check_variable = { which = hp_frontier_organization value >= 40 } }
  localization_key = haipam.org.stable }
 text = { trigger = { check_variable = { which = hp_frontier_organization value >= 20 } }
  localization_key = haipam.org.low }
 text = { localization_key = haipam.org.critical }
}
''')
loc={
 'NAME_HAIPAM_FRONTIER':'[haipam_secession_colony.GetName]舰团领',
 'decision_haipam_frontier_command':'边疆舰团事务',
 'decision_haipam_frontier_command_desc':'查看舰团组织度，暂停或恢复自动拓殖，支付经费整编边疆体系。只在首都使用。',
 'haipam_friendly_autonomy':'友好舰团自治',
 'haipam.org.high':'充足（70—100）','haipam.org.stable':'稳定（40—69）',
 'haipam.org.low':'偏低（20—39）','haipam.org.critical':'不足（0—19）',
 'haipam.301.name':'舰团向边疆延伸',
 'haipam.301.desc':'舰团化让独立开拓队成为可能。每年最多建立一座边疆哨站并启动一处殖民，必须支付实际经费。哨站只选择相邻、已勘测、无主且没有敌对舰队的星系；殖民还要求适居性达到60%。重力子神殿运作时停止签发新的开拓任务。\n\n首都的“边疆舰团事务”决议可管理拓殖和组织度。',
 'haipam.301.advance':'开始自动拓殖。','haipam.301.pause':'先暂停，保留开拓编制。',
 'haipam.310.name':'边疆舰团事务',
 'haipam.310.desc':'组织度：§Y[This.GetHaipamFrontierOrganization]§!。\n\n哨站经费：100合金、50影响力、100能量。殖民工程包：200合金、800矿物、300食物、200消费品、200能量，等待一年，包含孵化场和反应釜设备。\n\n组织度每年恢复5，建站消耗4，派出殖民团消耗6；神殿运作时每年额外恢复5。整编恢复25，五年内只能进行一次。组织度持续两年低于20时，成熟的自动殖民地可能友好独立。暂停只停止新任务，已经出发的殖民团继续行程。',
 'haipam.310.resume':'恢复自动拓殖。','haipam.310.pause':'暂停新的开拓任务。',
 'haipam.310.reorganize':'花费500凝聚力和500能量整编。','haipam.310.close':'结束会议。',
 'haipam.322.name':'边疆殖民团落地',
 'haipam.322.desc':'开拓团完成了一年的建设准备，新殖民地已并入帝国。孵化场和反应釜工程包已经安装；白蚊人负责开拓组织，灰蚊人仍按空缺岗位经过孵化周期补员。',
 'haipam.322.ok':'让殖民地开始生产。',
 'haipam.330.name':'边疆组织度偏低',
 'haipam.330.desc':'开拓速度开始超过指挥与补给体系的承受范围。继续推进可能让成熟边疆殖民地自行组成友好的舰团国家。母星、首都与手动建立的殖民地不在此次自动分裂范围内。现在可以整编或暂停新任务。',
 'haipam.330.manage':'召开边疆会议。','haipam.330.continue':'保持当前政策。',
 'haipam.331.name':'友好的分道而行',
 'haipam.331.desc':'[haipam_secession_colony.GetName]的开拓舰团提出并完成了独立建制。新成立的[haipam_frontier_child.GetName]接管该单殖民地星系，保留白蚊人与灰蚊人的制度，并继承现有科技。双方建立通讯、友好关系与停战，没有爆发叛乱战争。',
 'haipam.331.ok':'保持航线与联络。',
}
for language in ['english','simp_chinese']:
 p=MOD/f'localisation/{language}/haipam_frontier_l_{language}.yml'
 p.write_text('l_'+language+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'frontier':True,'delayed_colonization_days':360,'friendly_secession':True,
 'organization_management':True,'new_country_limit_per_parent':3,'gameplay_verified':False}))
