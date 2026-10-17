"""Crisis reform faction requested by the user; thresholds are prototypes."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'mod/haipam'
def put(rel,text):
 p=MOD/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

put('common/scripted_triggers/haipam_salvation_triggers.txt',r'''
haipam_salvation_food_crisis = {
 OR = { has_resource = { type = food amount < 200 } has_deficit = food }
}
haipam_salvation_crisis = {
 OR = {
  check_variable = { which = hp_salvation_hunger_months value >= 3 }
  has_country_flag = haipam_recent_defeat
 }
}
''')
put('common/pop_faction_types/haipam_salvation.txt',r'''
haipam_salvation = {
 election_header = "GFX_haipam_evt_royal_hall"
 guiding_ethic = ethic_authoritarian visual_ethic = "totalitarian_visual_ethic"
 use_guiding_ethic_as_pop_filter = no use_guiding_ethic_as_growth_factor = no
 pop_ethics_filter = { ethic_authoritarian ethic_egalitarian ethic_militarist ethic_pacifist ethic_materialist ethic_spiritualist ethic_xenophile ethic_xenophobe }
 unique = yes can_rename = no persistent_faction = yes skip_creation_cooldown = yes
 support_multiplier = 1
 resources = { category = pop_factions inline_script = pop_faction_types/shared_unity_production }
 is_potential = {
  haipam_is_empire = yes has_country_flag = haipam_salvation_unlocked
 }
 can_join_pre_triggers = { is_enslaved = no is_being_purged = no }
 can_join_faction = { pop_group_has_trait = trait_haipam_white has_citizenship_rights = yes }
 attraction = {
  base = 100
  modifier = { factor = 3 owner = { haipam_salvation_crisis = yes } }
 }
 leader = {
  base = 100
  modifier = { factor = 0 species = { NOT = { has_trait = trait_haipam_white } } }
  modifier = { factor = 0 is_event_leader = yes }
 }
 demand = {
  title = HAIPAM_SALVATION_GRAIN unfulfilled_title = HAIPAM_SALVATION_NO_GRAIN desc = HAIPAM_SALVATION_GRAIN_DESC
  fulfilled_effect = 10 unfulfilled_effect = -20
  potential = { exists = owner }
  trigger = { owner = { has_resource = { type = food amount >= 1000 } NOT = { has_deficit = food } } }
 }
 demand = {
  title = HAIPAM_SALVATION_RECOVERY unfulfilled_title = HAIPAM_SALVATION_DEFEAT desc = HAIPAM_SALVATION_RECOVERY_DESC
  fulfilled_effect = 5 unfulfilled_effect = -10
  potential = { exists = owner }
  trigger = { owner = { NOT = { has_country_flag = haipam_recent_defeat } } }
 }
 demand = {
  title = HAIPAM_SALVATION_INDUSTRY unfulfilled_title = HAIPAM_SALVATION_NO_INDUSTRY desc = HAIPAM_SALVATION_INDUSTRY_DESC
  fulfilled_effect = 5 unfulfilled_effect = -10
  potential = { exists = owner }
  trigger = { owner = { any_owned_planet = { has_active_building = building_haipam_royal_design_bureau } } }
 }
 demand = {
  title = HAIPAM_SALVATION_REFORM unfulfilled_title = HAIPAM_SALVATION_NO_REFORM desc = HAIPAM_SALVATION_REFORM_DESC
  fulfilled_effect = 10 unfulfilled_effect = -5
  potential = { exists = owner }
  trigger = { owner = { has_country_flag = haipam_salvation_reform_active } }
 }
 on_create = {
  set_name = "NAME_HAIPAM_SALVATION"
  owner = {
   set_country_flag = haipam_salvation_formed
   if = { limit = { is_ai = no } country_event = { id = haipam.621 days = 1 } }
  }
 }
 actions = {
  haipam_salvation_fund_reform = {
   title = HAIPAM_SALVATION_FUND_REFORM description = HAIPAM_SALVATION_FUND_REFORM_DESC
   potential = { owner = { haipam_is_empire = yes } }
   valid = { owner = { NOT = { has_country_flag = haipam_salvation_reform_active }
    has_resource = { type = energy amount >= 1000 } has_resource = { type = unity amount >= 500 } } }
   effect = { owner = { add_resource = { energy = -1000 unity = -500 }
    set_timed_country_flag = { flag = haipam_salvation_reform_active days = 1800 }
    add_modifier = { modifier = haipam_salvation_reform days = 1800 } } }
   ai_weight = { base = 10 }
  }
 }
}
''')
put('common/static_modifiers/haipam_salvation_modifiers.txt',r'''
haipam_salvation_reform = {
 planet_jobs_food_produces_mult = 0.25 planet_stability_add = 5
}
''')
put('events/haipam_salvation_events.txt',r'''
namespace = haipam
country_event = {
 id = haipam.620 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes }
 immediate = {
  if = { limit = { haipam_salvation_food_crisis = yes }
   change_variable = { which = hp_salvation_hunger_months value = 1 } }
  else = { set_variable = { which = hp_salvation_hunger_months value = 0 } }
  if = { limit = { NOT = { has_country_flag = haipam_salvation_unlocked } haipam_salvation_crisis = yes }
   random_list = { 90 = { } 10 = {
    set_country_flag = haipam_salvation_unlocked
    enable_faction_of_type = haipam_salvation
   } }
  }
  if = { limit = { has_country_flag = haipam_salvation_unlocked NOT = { has_country_flag = haipam_salvation_formed } }
   enable_faction_of_type = haipam_salvation }
 }
}
country_event = {
 id = haipam.622 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes }
 immediate = { set_timed_country_flag = { flag = haipam_recent_defeat days = 3600 } }
}
country_event = {
 id = haipam.621 is_triggered_only = yes title = haipam.621.name desc = haipam.621.desc
 picture = GFX_haipam_evt_royal_hall option = { name = haipam.621.ok }
}
''')
put('common/on_actions/haipam_salvation_on_actions.txt',r'''
on_monthly_pulse_country = { events = { haipam.620 } }
on_war_lost = { events = { haipam.622 } }
''')
loc={
 'haipam_salvation':'海帕姆救国会','haipam_salvation_desc':'由白蚊人组织的危机改革派，主张保障粮食、恢复生产并整顿帝国。',
 'NAME_HAIPAM_SALVATION':'海帕姆救国会',
 'HAIPAM_SALVATION_GRAIN':'粮仓充足','HAIPAM_SALVATION_NO_GRAIN':'粮食保障不足',
 'HAIPAM_SALVATION_GRAIN_DESC':'救国会要求至少1000食物储备，并结束粮食短缺。',
 'HAIPAM_SALVATION_RECOVERY':'恢复国家信心','HAIPAM_SALVATION_DEFEAT':'战败后的整顿',
 'HAIPAM_SALVATION_RECOVERY_DESC':'战败后的十年被视为恢复期，救国会要求帝国重建生产与国防。',
 'HAIPAM_SALVATION_INDUSTRY':'皇家工业重整','HAIPAM_SALVATION_NO_INDUSTRY':'缺乏工业重整机构',
 'HAIPAM_SALVATION_INDUSTRY_DESC':'至少维持一座正常运作的皇家设计局。',
 'HAIPAM_SALVATION_REFORM':'改革计划执行中','HAIPAM_SALVATION_NO_REFORM':'要求拨付改革经费',
 'HAIPAM_SALVATION_REFORM_DESC':'通过派系行动拨款，开展五年的粮食统筹和地方整顿。',
 'HAIPAM_SALVATION_FUND_REFORM':'拨款开展救国整顿',
 'HAIPAM_SALVATION_FUND_REFORM_DESC':'支付1000能量和500凝聚力，五年内农业岗位产出+25%，行星稳定度+5。',
 'haipam_salvation_reform':'救国整顿计划',
 'haipam.621.name':'海帕姆救国会成立',
 'haipam.621.desc':'危机让一批白蚊人官员、生产组织者与退役军官联合起来，组成海帕姆救国会。他们要求保障粮食供应、恢复生产，并以改革计划整顿帝国。派系已进入政治界面，可以查看诉求并拨付整顿经费。',
 'haipam.621.ok':'将他们的诉求提交议程。',
}
for lang in ['english','simp_chinese']:
 (MOD/f'localisation/{lang}/haipam_salvation_l_{lang}.yml').write_text('l_'+lang+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in loc.items()),encoding='utf-8-sig')
print(json.dumps({'faction':'haipam_salvation','chance_per_crisis_month':0.10,'hunger_months_required':3,'gameplay_verified':False}))
