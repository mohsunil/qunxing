"""Author Haipam gameplay additions without replacing the population pipeline.

All balance numbers below are prototype proposals, not canonical requirements.
Do not copy or ship base-game source/assets with this module.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/haipam'
def put(rel,text):
    p=MOD/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8')

techs=[
 ('tech_haipam_royal_biology','society','biology',1,1500,['tech_genome_mapping'],'BIOLOGICAL_species_trait_points_add = 2 modify_species_cost_mult = -0.90'),
 ('tech_haipam_royal_governance','society','statecraft',2,4000,['tech_planetary_government'],''),
 ('tech_haipam_royal_design','engineering','industry',1,1800,['tech_engineering_1'],''),
 ('tech_haipam_fleetization','society','military_theory',2,5000,['tech_doctrine_fleet_size_1'],'command_limit_add = -20 country_naval_cap_add = 200 country_naval_cap_mult = 0.50 ships_upkeep_mult = -0.70 ship_build_speed_mult = 0.50'),
 ('tech_haipam_postal_fleets','society','statecraft',1,2000,['tech_interplanetary_commerce'],'planet_jobs_trade_produces_mult = 0.50 country_trade_produces_mult = 0.25'),
 ('tech_haipam_axial_small','physics','particles',2,3500,['tech_plasma_1'],''),
 ('tech_haipam_axial_medium','physics','particles',3,8000,['tech_haipam_axial_small'],''),
 ('tech_haipam_axial_heavy','physics','particles',4,16000,['tech_haipam_axial_medium'],''),
 ('tech_haipam_graviton_cult','society','psionics',2,5000,['tech_psionic_theory'],''),
 ('tech_haipam_dual_helix','society','biology',3,10000,['tech_gene_tailoring','tech_haipam_graviton_cult'],'BIOLOGICAL_species_trait_points_add = 4'),
 ('tech_haipam_planetary_arsenal','engineering','voidcraft',4,20000,['tech_mega_engineering','tech_haipam_fleetization'],'starbase_shipyard_build_speed_mult = 0.25'),
]
parts=[]
for key,area,category,tier,cost,prereq,modifier in techs:
    parts.append(f'''{key} = {{
 area = {area} category = {{ {category} }} tier = {tier} cost = {cost} weight = 100
 prerequisites = {{ {' '.join('"'+p+'"' for p in prereq)} }}
 potential = {{ has_valid_civic = civic_haipam_royal_biology }}
 modifier = {{ {modifier} }}
 ai_weight = {{ factor = 2 }}
}}''')
put('common/technology/haipam_technologies.txt','\n\n'.join(parts))

put('common/buildings/haipam_advanced_buildings.txt',r'''
building_haipam_royal_hall = {
 icon = building_haipam_royal_hall
 capital = yes capital_tier = 4 position_priority = 0
 can_build = no can_demolish = no can_be_ruined = no can_be_disabled = no
 category = government building_sets = { government } planet_limit = 1
 potential = { is_capital = yes exists = owner owner = { haipam_is_empire = yes } }
 prerequisites = { "tech_haipam_royal_governance" }
 planet_modifier = { planet_housing_add = 4000 planet_amenities_add = 4000 planet_stability_add = 10 }
 inline_script = { script = buildings/on_all_capital_buildings }
 inline_script = { script = buildings/regular_empire_capital_jobs AMOUNT = 400 }
 resources = { category = planet_buildings upkeep = { energy = 12 } produces = { unity = 100 } }
}
building_haipam_royal_design_bureau = {
 icon = building_haipam_royal_design_bureau base_buildtime = 480
 category = research building_sets = { urban research } planet_limit = 1
 potential = { exists = owner owner = { haipam_is_empire = yes } }
 allow = { has_upgraded_capital = yes }
 prerequisites = { "tech_haipam_royal_design" }
 planet_modifier = { job_physicist_add = 300 job_engineer_add = 300 }
 resources = { category = planet_buildings cost = { minerals = 700 alloys = 150 }
 upkeep = { energy = 8 consumer_goods = 4 } produces = { physics_research = 30 engineering_research = 30 } }
}
building_haipam_graviton_temple = {
 icon = building_haipam_graviton_temple base_buildtime = 600
 category = unity building_sets = { government urban } planet_limit = 1
 potential = { exists = owner owner = { haipam_is_empire = yes has_country_flag = haipam_ling_unlocked } }
 prerequisites = { "tech_haipam_graviton_cult" }
 planet_modifier = { job_bureaucrat_add = 300 job_trader_add = 200 }
 resources = { category = planet_buildings cost = { minerals = 1000 alloys = 200 }
 upkeep = { energy = 10 consumer_goods = 5 } produces = { unity = 80 trade = 35 } }
}
building_haipam_postal_hub = {
 icon = building_haipam_postal_hub base_buildtime = 300
 category = trade building_sets = { urban trade } planet_limit = 1
 potential = { exists = owner owner = { haipam_is_empire = yes } }
 prerequisites = { "tech_haipam_postal_fleets" }
 planet_modifier = { job_trader_add = 200 }
 resources = { category = planet_buildings cost = { minerals = 500 alloys = 100 }
 upkeep = { energy = 5 } produces = { trade = 30 } }
}
''')

put('common/traits/haipam_advanced_traits.txt',r'''
leader_trait_haipam_royal_continuity = {
 leader_class = { scientist commander official }
 initial = no randomized = no notify_on_gained = no immortal_leaders = yes
 icon = { layer = { icon = "GFX_haipam_royal_continuity" } }
}
trait_haipam_ling = {
 cost = 0 initial = no randomized = no allowed_archetypes = { BIOLOGICAL }
 species_potential_add = { always = no } species_possible_remove = { always = no }
 species_possible_merge_remove = { always = no }
 icon = "gfx/interface/icons/haipam/trait_haipam_ling.dds"
 modifier = { planet_jobs_unity_produces_mult = 0.50 planet_jobs_trade_produces_mult = 0.25 }
}
''')

put('common/decisions/haipam_decisions.txt',r'''
decision_haipam_royal_hall = {
 icon = decision_planet_to_city_world
 owned_planets_only = yes enactment_time = 360
 potential = { is_capital = yes exists = owner owner = { haipam_is_empire = yes }
 NOT = { has_building = building_haipam_royal_hall } }
 allow = { owner = { has_technology = tech_haipam_royal_governance } has_upgraded_capital = yes }
 resources = { category = decisions cost = { alloys = 1000 minerals = 1500 unity = 500 } }
 effect = {
  if = { limit = { has_building = building_capital } remove_building = building_capital }
  if = { limit = { has_building = building_major_capital } remove_building = building_major_capital }
  if = { limit = { has_building = building_system_capital } remove_building = building_system_capital }
  add_building = building_haipam_royal_hall
  owner = { haipam_refresh_royal_continuity = yes country_event = { id = haipam.201 days = 1 } }
 }
 ai_weight = { weight = 10 }
}
decision_haipam_gray_gene_program = {
 icon = decision_genetic_experiment
 owned_planets_only = yes enactment_time = 30
 potential = { exists = owner owner = { haipam_is_empire = yes }
 has_active_building = building_haipam_royal_hatchery }
 allow = { owner = { has_technology = tech_haipam_royal_biology NOT = { has_country_flag = haipam_gray_gene_menu } }
 any_owned_pop_group = { haipam_is_gray_pop_group = yes } }
 resources = { category = decisions cost = { food = 500 alloys = 100 } }
 effect = { owner = { set_country_flag = haipam_gray_gene_menu country_event = { id = haipam.220 days = 1 } } }
 ai_weight = { weight = 0 }
}
''')

put('common/scripted_effects/haipam_progression.txt',r'''
# Country scope. Only the presence of an active royal capital grants immortality.
haipam_refresh_royal_continuity = {
 if = {
  limit = { any_owned_planet = { has_active_building = building_haipam_royal_hall } }
  every_owned_leader = { limit = { species = { has_trait = trait_haipam_white }
   NOT = { has_trait = leader_trait_haipam_royal_continuity } }
   add_trait = leader_trait_haipam_royal_continuity }
  every_pool_leader = { limit = { species = { has_trait = trait_haipam_white }
   NOT = { has_trait = leader_trait_haipam_royal_continuity } }
   add_trait = leader_trait_haipam_royal_continuity }
 }
 else = {
  every_owned_leader = { limit = { has_trait = leader_trait_haipam_royal_continuity }
   remove_trait = leader_trait_haipam_royal_continuity }
  every_pool_leader = { limit = { has_trait = leader_trait_haipam_royal_continuity }
   remove_trait = leader_trait_haipam_royal_continuity }
 }
}

# Country scope. One-time separate species; the white lineage marker preserves
# white-only leadership, rather than turning gray workers into eligible leaders.
haipam_awaken_ling = {
 set_country_flag = haipam_ling_unlocked
 create_species = {
  name = "HAIPAM_LING" plural = "HAIPAM_LING" adjective = "HAIPAM_LING"
  class = ART portrait = haipam_white_02
  traits = { trait = trait_organic trait = trait_haipam_white trait = trait_haipam_ling trait = trait_psionic }
  effect = { save_event_target_as = haipam_new_ling }
 }
 event_target:haipam_new_ling = { set_citizenship_type = { country = root type = citizenship_full } }
 capital_scope = { create_pop_group = { species = event_target:haipam_new_ling category = specialist size = 200 } }
 country_event = { id = haipam.211 days = 1 }
}

# One mutually exclusive production specialization (all three cost two points).
# Existing non-program gene changes and the gray lineage marker are preserved.
haipam_gray_gene_program = {
 every_owned_species = {
  limit = { has_trait = trait_haipam_gray NOT = { has_trait = $TRAIT$ } }
  save_event_target_as = haipam_gene_old
  modify_species = {
   species = this
   remove_trait = trait_industrious remove_trait = trait_agrarian remove_trait = trait_intelligent
   add_trait = $TRAIT$
   effect = { save_event_target_as = haipam_gene_new }
  }
  event_target:haipam_gene_new = { set_citizenship_type = { country = root type = citizenship_limited } }
  root = { every_owned_planet = { every_owned_pop_group = {
   limit = { is_exact_same_species = event_target:haipam_gene_old }
   change_species = event_target:haipam_gene_new
  } } }
 }
 remove_country_flag = haipam_gray_gene_menu
}
''')

put('events/haipam_progression_events.txt',r'''
namespace = haipam
country_event = {
 id = haipam.200 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes }
 immediate = {
  haipam_refresh_royal_continuity = yes
  if = { limit = { has_technology = tech_psionic_theory NOT = { has_country_flag = haipam_ling_unlocked } }
   haipam_awaken_ling = yes }
 }
}
country_event = {
 id = haipam.201 is_triggered_only = yes title = haipam.201.name desc = haipam.201.desc
 picture = GFX_haipam_evt_royal_hall
 option = { name = haipam.201.ok }
}
country_event = {
 id = haipam.211 is_triggered_only = yes title = haipam.211.name desc = haipam.211.desc
 picture = GFX_haipam_evt_ling
 option = { name = haipam.211.ok }
}
country_event = {
 id = haipam.220 is_triggered_only = yes title = haipam.220.name desc = haipam.220.desc
 picture = GFX_haipam_evt_hatchery
 option = { name = haipam.220.industry haipam_gray_gene_program = { TRAIT = trait_industrious } }
 option = { name = haipam.220.food haipam_gray_gene_program = { TRAIT = trait_agrarian } }
 option = { name = haipam.220.research haipam_gray_gene_program = { TRAIT = trait_intelligent } }
 option = { name = haipam.220.cancel remove_country_flag = haipam_gray_gene_menu }
}
# Low-frequency temple experiences, gated by the completed temple rather than
# merely researching psionics. They add resources/modifiers, never console cheats.
country_event = {
 id = haipam.230 hide_window = yes is_triggered_only = yes
 trigger = { haipam_is_empire = yes any_owned_planet = { has_active_building = building_haipam_graviton_temple } }
 immediate = { random_list = { 70 = { } 15 = { country_event = { id = haipam.231 days = 5 } }
 15 = { country_event = { id = haipam.232 days = 5 } } } }
}
country_event = {
 id = haipam.231 is_triggered_only = yes title = haipam.231.name desc = haipam.231.desc
 picture = GFX_haipam_evt_ling
 option = { name = haipam.231.harmony add_resource = { unity = 600 } }
 option = { name = haipam.231.insight add_resource = { society_research = 1000 } }
}
country_event = {
 id = haipam.232 is_triggered_only = yes title = haipam.232.name desc = haipam.232.desc
 picture = GFX_haipam_evt_ling
 option = { name = haipam.232.trade add_modifier = { modifier = haipam_graviton_trade days = 1080 } }
 option = { name = haipam.232.guard add_modifier = { modifier = haipam_graviton_guard days = 1080 } }
}
''')

put('common/static_modifiers/haipam_modifiers.txt',r'''
haipam_graviton_trade = { country_trade_produces_mult = 0.50 }
haipam_graviton_guard = { ship_hull_mult = 0.25 army_health = 0.50 }
''')
put('common/armies/haipam_armies.txt',r'''
haipam_ling_guard = {
 damage = 4.0 morale_damage = 3.0 health = 4.0 morale = 5.0
 collateral_damage = 0.25 war_exhaustion = 2.0 time = 90 icon = GFX_army_type_haipam_ling
 prerequisites = { "tech_haipam_graviton_cult" }
 resources = { category = armies cost = { minerals = 250 alloys = 50 } upkeep = { energy = 1 } }
 potential_country = { haipam_is_empire = yes }
 potential = { from = { has_trait = trait_haipam_ling } }
 allow = { has_active_building = building_haipam_graviton_temple }
 ai_weight = { base = 100 }
}
''')

put('common/on_actions/haipam_progression_on_actions.txt',r'''
on_monthly_pulse_country = { events = { haipam.200 } }
on_tech_increased = { events = { haipam.200 } }
on_yearly_pulse_country = { events = { haipam.230 } }
''')

# Add/replace only our new localization keys; preserve all previous translations.
loc={
'tech_haipam_royal_biology':('皇家生物工程','开放灰蚊人皇家模板程序；原版生物改造项目成本降低90%，生物特质点数+2。原型数值。'),
'tech_haipam_royal_governance':('军耀殿制度','开放首都改造决议，将帝国首都升级为军耀殿，维系白蚊人领袖的持续生命。'),
'tech_haipam_royal_design':('皇家设计局','开放皇家设计局，提供物理学与工程学专门岗位和基础研究产出。'),
'tech_haipam_fleetization':('舰团化','小型舰团协同作战：降低单舰队指挥上限，提高帝国海军容量并大幅降低维护。'),
'tech_haipam_postal_fleets':('邮政舰队','贸易航线承担运输与船只回收。开放邮政枢纽，提高贸易产出；邮政枢纽运作期间，每年可能找到需要维修的旧式轴炮舰。'),
'tech_haipam_axial_small':('小型等离子轴炮','开放小型轴向等离子武器。'),
'tech_haipam_axial_medium':('中型等离子轴炮','开放中型轴向等离子武器。'),
'tech_haipam_axial_heavy':('重型等离子轴炮','开放重型轴向等离子武器。'),
'tech_haipam_graviton_cult':('重力子神殿','开放灵蚊人专属军队、神殿与灵能事件。灵蚊人的初次出现由灵能理论触发。'),
'tech_haipam_dual_helix':('王家双螺旋','皇家生物工程与灵能研究并行发展，额外生物特质点数+4。原版飞升互斥规则尚未改写。'),
'tech_haipam_planetary_arsenal':('海帕姆行星兵工厂','开放母星分阶段舰造工程，提升舰船生产速度。'),
'building_haipam_royal_hall':('军耀殿','首都政治与指挥中心。产出大量凝聚力；建筑运作期间，帝国及候选池中的白蚊人领袖获得不朽。'),
'building_haipam_royal_design_bureau':('皇家设计局','增加物理学家与工程师岗位，并直接产出物理学与工程学研究。空缺专家岗位由皇家孵化场按需补员。'),
'building_haipam_graviton_temple':('重力子神殿','灵蚊人的研究与礼仪设施。产出凝聚力、贸易，开放神殿事件及灵蚊人卫队招募。'),
'building_haipam_postal_hub':('皇家邮政枢纽','邮政舰队的补给与货运枢纽，提供商贸岗位和贸易产出。'),
'decision_haipam_royal_hall':('建设军耀殿','花费一年将当前首都建筑改造为军耀殿。此决议替换现有首都建筑。'),
'decision_haipam_gray_gene_program':('皇家灰蚊人模板程序','30天完成准备，选择工业、农业或科研专精，应用于帝国所有灰蚊人基因变体。三种程序相互替换；保留其他非程序基因。'),
'leader_trait_haipam_royal_continuity':('军耀殿·王家续生','军耀殿运作期间获得无限自然寿命，仍可因战斗和剧情事件死亡。'),
'trait_haipam_ling':('灵蚊人','白蚊人谱系中的灵能种族。凝聚力与贸易专长，保留白蚊人领袖资格。'),
'haipam_ling_guard':('灵蚊人卫队','重力子神殿训练的专属灵能地面部队。'),
'HAIPAM_LING':('灵蚊人','灵蚊人'),
'haipam_graviton_trade':('重力子·贸易回声','神殿回声提高帝国贸易产出。'),
'haipam_graviton_guard':('重力子·卫御回声','神殿回声提高舰体与军队耐久。'),
}
events={
'haipam.201.name':'军耀殿落成','haipam.201.desc':'军耀殿的续生系统开始运转。白蚊人领袖的神经档案与再生组织在此持续维护，帝国的行政、研究与军令获得长期延续。','haipam.201.ok':'让帝国的意志延续。',
'haipam.211.name':'第一批灵蚊人','haipam.211.desc':'灵能理论突破后，皇家研究记录确认了新的灵蚊人种族。首批灵蚊人已在首都出现，他们仍属于白蚊人谱系。重力子神殿将把这些潜能转化为稳定的社会制度。','haipam.211.ok':'继续研究重力子神殿。',
'haipam.220.name':'选择皇家模板','haipam.220.desc':'孵化场已完成快速改造准备。选择一种灰蚊人专精模板，替换此前的皇家生产专精；各变体的其他基因保持原样。','haipam.220.industry':'工业模板：勤勉。','haipam.220.food':'农业模板：农耕。','haipam.220.research':'科研模板：聪慧。','haipam.220.cancel':'暂时保留现有模板。',
'haipam.231.name':'神殿的合声','haipam.231.desc':'重力子神殿捕捉到一次稳定的集体灵能共振。我们可以把这一经验用于社会协作，或进一步研究意识与生物之间的联系。','haipam.231.harmony':'用于社会协作。','haipam.231.insight':'转入社会学研究。',
'haipam.232.name':'遥远的回声','haipam.232.desc':'灵蚊人的知觉沿着航线向外延伸。一些信号带来交换与联络的机会，另一些则让卫队提前察觉冲突。','haipam.232.trade':'关注贸易航线。','haipam.232.guard':'加强舰队与卫队。',
}
for key,(name,desc) in list(loc.items()):events[key]=name;events[key+'_desc']=desc
for language in ['english','simp_chinese']:
    path=MOD/f'localisation/{language}/haipam_gameplay_l_{language}.yml'
    path.write_text('l_'+language+':\n'+''.join(' '+k+':0 '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in events.items()),encoding='utf-8-sig')
print(json.dumps({'technologies':len(techs),'new_buildings':4,'new_army':1,'new_decisions':2,'runtime_verified':False}))
