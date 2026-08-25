# -*- coding: utf-8 -*-
"""新装备技能（技能ID -100 起，定义见 utils/equipment_skills.py）。

主动技能均为玩家先手；被动技能通过事件监听实现。
"""
from skills.registry import register_active, register_passive


# ================= 主动技能 =================
@register_active('亘古庇佑', first_strike=True)
def ancient_protection(engine, skill):
    engine.apply_buff_effect(engine.player, {'name': '亘古庇佑', 'stat': 'damage_reduce_percent', 'amount': 100}, 2)
    engine.log.append("亘古庇佑！最终受伤减免100%（2回合）")
    return True


@register_active('光阴疾斩', first_strike=True)
def time_slash(engine, skill):
    dmg = engine.hit_monster_normal(
        engine.player.attack * 1.3 + engine.player.agility * 0.65 + engine.player.max_energy * 0.5)
    engine.apply_buff_effect(engine.player, {'name': '光阴疾斩·必中', 'stat': 'sure_hit', 'amount': 0}, 1)
    engine.log.append(f"光阴疾斩！造成 {round(dmg)} 点伤害，必中1回合")
    return True


@register_active('吞噬', first_strike=True)
def devour(engine, skill):
    dmg = round((engine.player.max_energy + engine.player.max_hp) * 0.1, 2)
    engine.hit_monster_true(dmg)
    engine.apply_buff_effect(engine.monster, {'name': '吞噬·眩晕', 'stat': 'stun', 'amount': 0}, 2, is_debuff=True)
    engine.log.append(f"吞噬！造成 {round(dmg)} 点真实伤害，眩晕2回合")
    return True


@register_active('哀霜咏叹', first_strike=True)
def frost_elegy(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack + engine.player.max_energy * 0.8)
    v = round(15 + engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.monster, {'name': '哀霜咏叹·防御', 'stat': 'defense_percent', 'amount': -v}, 5, is_debuff=True)
    engine.apply_buff_effect(engine.monster, {'name': '哀霜咏叹·敏捷', 'stat': 'agility_percent', 'amount': -v}, 5, is_debuff=True)
    engine.log.append(f"哀霜咏叹！造成 {round(dmg)} 点伤害，敌方防御/敏捷-{v:.2f}%（5回合）")
    return True


@register_active('回溯织线', first_strike=True)
def rewind_weave(engine, skill):
    engine.heal_player(round(engine.player.max_hp * 0.2 + engine.player.max_energy * 0.1, 2), '回溯织线')
    v = round(20 + engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.player, {'name': '回溯织线·减伤', 'stat': 'damage_reduce_percent', 'amount': v}, 3)
    engine.log.append(f"回溯织线：最终受伤-{v:.2f}%（3回合）")
    return True


@register_active('封灵暗幕', first_strike=True)
def sealing_veil(engine, skill):
    v = round(15 + engine.player.max_energy * 0.02, 2)
    engine.apply_buff_effect(engine.monster, {'name': '封灵暗幕·攻击', 'stat': 'attack_percent', 'amount': -v}, 5, is_debuff=True)
    engine.apply_buff_effect(engine.monster, {'name': '封灵暗幕·减疗', 'stat': 'heal_reduce', 'amount': 40}, 5, is_debuff=True)
    engine.log.append(f"封灵暗幕！敌方攻击-{v:.2f}%、治疗-40%（5回合）")
    return True


@register_active('山崩地裂', first_strike=True)
def mountain_collapse(engine, skill):
    engine.apply_buff_effect(engine.monster, {'name': '山崩地裂·敏捷', 'stat': 'agility_percent', 'amount': -50}, 10, is_debuff=True)
    dmg = engine.hit_monster_normal(engine.player.max_hp * 0.8)
    engine.log.append(f"山崩地裂！敌方敏捷-50%（10回合），造成 {round(dmg)} 点伤害")
    return True


@register_active('无量通行', first_strike=True)
def infinite_passage(engine, skill):
    v = round(10 + engine._get_gear_level('饰品'), 2)
    engine.apply_buff_effect(engine.player, {'name': '无量通行·敏捷', 'stat': 'agility_percent', 'amount': v}, 3)
    engine.apply_buff_effect(engine.player, {'name': '无量通行·必中', 'stat': 'sure_hit', 'amount': 0}, 3)
    engine.log.append(f"无量通行！敏捷+{v:.2f}%，必中（3回合）")
    return True


@register_active('日耀审判', first_strike=True)
def solar_judgment(engine, skill):
    dmg = engine.hit_monster_normal(
        engine.player.attack * 1.3 + engine.player.crit * 1.2 + engine.player.pen + engine.player.max_energy * 0.5)
    v = round(5 + engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.player, {'name': '日耀审判·增伤', 'stat': 'final_damage', 'amount': v}, 2)
    engine.log.append(f"日耀审判！造成 {round(dmg)} 点伤害，最终伤害+{v:.2f}%（2回合）")
    return True


@register_active('日耀裁决', first_strike=True)
def solar_verdict(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.35 + engine.player.pen + engine.player.max_energy * 0.5)
    true_dmg = round(engine.turn_count * 4, 2)
    engine.hit_monster_true(true_dmg)
    v = round(5 + engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.player, {'name': '日耀裁决·增伤', 'stat': 'final_damage', 'amount': v}, 2)
    engine.log.append(f"日耀裁决！造成 {round(dmg)} 点伤害+{round(true_dmg)}真伤，最终伤害+{v:.2f}%（2回合）")
    return True


@register_active('暴食', first_strike=True)
def gluttony(engine, skill):
    cost = round(engine.player.hp * 0.1, 2)
    engine.player.hp = max(1, round(engine.player.hp - cost, 2))
    v = round(engine.player.max_energy * 0.03, 2)
    engine.apply_buff_effect(engine.player, {'name': '暴食·攻击', 'stat': 'attack_percent', 'amount': v}, 10)
    engine.apply_buff_effect(engine.player, {'name': '暴食·暴击', 'stat': 'crit_percent', 'amount': v}, 10)
    regen = round(engine.player.max_energy * 0.02, 2)
    engine.apply_buff_effect(engine.player, {'name': '暴食·恢复', 'stat': 'regen', 'amount': regen}, 10)
    engine.log.append(f"暴食！消耗 {round(cost)} 生命，攻击/暴击+{v:.2f}%，每回合恢复{round(regen)}（10回合）")
    return True


@register_active('月华秘钥', first_strike=True)
def moonlight_key(engine, skill):
    engine.heal_player(round(engine.player.max_hp * 0.1 + engine.player.max_energy * 0.25, 2), '月华秘钥')
    v = round(15 + engine.player.max_energy * 0.015, 2)
    engine.apply_buff_effect(engine.player, {'name': '月华秘钥·减伤', 'stat': 'damage_reduce_percent', 'amount': v}, 5)
    engine.log.append(f"月华秘钥：最终受伤-{v:.2f}%（5回合）")
    return True


@register_active('沸血之毒', first_strike=True)
def boiling_blood(engine, skill):
    bonus = round(engine.player.attack * 0.03, 2)
    engine.apply_buff_effect(engine.player, {'name': '沸血之毒', 'stat': 'bonus_true', 'amount': bonus}, -1)
    dmg = round(engine.player.max_energy * 0.1, 2)
    engine.hit_monster_true(dmg)
    v = round(engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.monster, {'name': '沸血之毒·终伤降', 'stat': 'final_damage', 'amount': -v}, 100, is_debuff=True)
    engine.log.append(f"沸血之毒！获得{round(bonus)}真伤附伤，造成{round(dmg)}伤害，敌方最终伤害-{v:.2f}%（100回合）")
    return True


@register_active('深渊暴动', first_strike=True)
def abyss_riot(engine, skill):
    bonus_true = round(engine.player.agility * 0.1, 2)
    engine.apply_buff_effect(engine.player, {'name': '深渊暴动·终伤', 'stat': 'final_damage', 'amount': 30}, 6)
    engine.apply_buff_effect(engine.player, {'name': '深渊暴动·敏捷', 'stat': 'agility_percent', 'amount': 50}, 6)
    engine.apply_buff_effect(engine.player, {'name': '深渊暴动·附伤', 'stat': 'bonus_true', 'amount': bonus_true}, 6)
    engine.log.append(f"深渊暴动！暴走6回合：最终伤害+30%、敏捷+50%，普攻附{round(bonus_true)}真伤")
    return True


@register_active('灵风', first_strike=True)
def spirit_wind(engine, skill):
    engine.apply_buff_effect(engine.monster, {'name': '灵风·眩晕', 'stat': 'stun', 'amount': 0}, 2, is_debuff=True)
    engine.log.append("灵风！眩晕敌方2回合")
    return True


@register_active('灼炎领域', first_strike=True)
def blazing_domain(engine, skill):
    bonus_flat = round(engine.player.attack * 0.5, 2)
    bonus_true = round(engine.player.max_energy * 0.1, 2)
    engine.apply_buff_effect(engine.player, {'name': '灼炎领域·附伤', 'stat': 'bonus_flat', 'amount': bonus_flat}, 8)
    engine.apply_buff_effect(engine.player, {'name': '灼炎领域·真伤', 'stat': 'bonus_true', 'amount': bonus_true}, 8)
    engine.apply_buff_effect(engine.monster, {'name': '灼炎领域·重伤', 'stat': 'heal_reduce', 'amount': 50}, 8, is_debuff=True)
    engine.log.append(f"灼炎领域！普攻附{round(bonus_flat)}伤害+{round(bonus_true)}真伤，敌方重伤（8回合）")
    return True


@register_active('爆裂', first_strike=True)
def detonate(engine, skill):
    dmg = engine.hit_monster_normal(
        engine.player.attack + engine.player.crit * 0.1 + engine.player.pen * 0.1 + engine.player.defense * 0.3)
    engine.log.append(f"爆裂！造成 {round(dmg)} 点伤害")
    return True


@register_active('疾焰突袭', first_strike=True)
def blaze_rush(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.1 + engine.player.agility * 0.8 + engine.player.max_energy * 0.2)
    engine.apply_buff_effect(engine.player, {'name': '疾焰突袭·敏捷', 'stat': 'agility_percent', 'amount': 15}, 2)
    engine.log.append(f"疾焰突袭！造成 {round(dmg)} 点伤害，敏捷+15%（2回合）")
    return True


@register_active('瘟骨压迫', first_strike=True)
def plague_oppress(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 2 + engine.player.max_hp * 0.08)
    engine.apply_buff_effect(engine.monster, {'name': '瘟骨压迫·减疗', 'stat': 'heal_reduce', 'amount': 50}, 6, is_debuff=True)
    engine.log.append(f"瘟骨压迫！造成 {round(dmg)} 点伤害，敌方治疗-50%（6回合）")
    return True


@register_active('瘟骨裂击', first_strike=True)
def plague_crack(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.5 + engine.player.max_hp * 0.05 + engine.player.max_energy * 0.4)
    v = round(35 + engine.player.max_energy * 0.02, 2)
    engine.apply_buff_effect(engine.monster, {'name': '瘟骨裂击·减疗', 'stat': 'heal_reduce', 'amount': v}, 5, is_debuff=True)
    engine.log.append(f"瘟骨裂击！造成 {round(dmg)} 点伤害，敌方治疗-{v:.2f}%（5回合）")
    return True


@register_active('盛怒绽放', first_strike=True)
def rage_bloom(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.25 + engine.player.energy * 3)
    heal = engine.heal_player(round((engine.player.max_hp - engine.player.hp) * 0.25, 2), '盛怒绽放')
    v = round(engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.player, {'name': '盛怒绽放·防御', 'stat': 'defense_percent', 'amount': v}, 10)
    engine.log.append(f"盛怒绽放！造成 {round(dmg)} 点伤害，恢复{round(heal)}生命，防御+{v:.2f}%（10回合）")
    return True


@register_active('瞬时偏移', first_strike=True)
def instant_shift(engine, skill):
    engine.apply_buff_effect(engine.player, {'name': '瞬时偏移·必闪', 'stat': 'sure_dodge', 'amount': 0}, 1)
    engine.apply_buff_effect(engine.player, {'name': '瞬时偏移·敏捷', 'stat': 'agility_percent', 'amount': 20}, 3)
    engine.log.append("瞬时偏移！必闪1回合，敏捷+20%（3回合）")
    return True


@register_active('繁荣不息', first_strike=True)
def prosperity(engine, skill):
    heal_now = engine.heal_player(round(engine.player.max_hp * 0.03, 2), '繁荣不息')
    regen = round(engine.player.max_hp * 0.001 * engine._get_gear_level('护甲'), 2)
    engine.apply_buff_effect(engine.player, {'name': '繁荣不息·恢复', 'stat': 'regen', 'amount': regen}, 30)
    engine.log.append(f"繁荣不息！立即恢复{round(heal_now)}，每回合恢复{round(regen)}（30回合）")
    return True


@register_active('蓄势', first_strike=True)
def power_charge(engine, skill):
    v1 = round(100 + engine.player.max_energy * 0.01, 2)
    v2 = round(engine.player.max_energy * 0.05, 2)
    engine.apply_buff_effect(engine.player, {'name': '蓄势·增伤', 'stat': 'final_damage', 'amount': v1}, 1)
    engine.apply_buff_effect(engine.player, {'name': '蓄势·减伤', 'stat': 'damage_reduce_percent', 'amount': v2}, 1)
    engine.log.append(f"蓄势！最终伤害+{v1:.2f}%，最终受伤-{v2:.2f}%（1回合）")
    return True


@register_active('虚化', first_strike=True)
def phasing(engine, skill):
    engine.apply_buff_effect(engine.player, {'name': '虚化·必闪', 'stat': 'sure_dodge', 'amount': 0}, 1)
    engine.apply_buff_effect(engine.player, {'name': '虚化·敏捷', 'stat': 'agility_percent', 'amount': 25}, 5)
    engine.log.append("虚化！必闪1回合，敏捷+25%（5回合）")
    return True


@register_active('裂岩契约', first_strike=True)
def rock_contract(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.3 + engine.player.defense * 0.6 + engine.player.max_energy * 0.2)
    engine.apply_buff_effect(engine.monster, {'name': '裂岩契约·防御', 'stat': 'defense_percent', 'amount': -12}, 3, is_debuff=True)
    engine.log.append(f"裂岩契约！造成 {round(dmg)} 点伤害，敌方防御-12%（3回合）")
    return True


@register_active('裂鳞护体', first_strike=True)
def scale_guard(engine, skill):
    engine.heal_player(round(engine.player.max_hp * 0.08 + engine.player.max_energy * 0.2, 2), '裂鳞护体')
    engine.apply_buff_effect(engine.player, {'name': '裂鳞护体·减伤', 'stat': 'damage_reduce_percent', 'amount': 10}, 3)
    engine.log.append("裂鳞护体：最终受伤-10%（3回合）")
    return True


@register_active('赤鳞复燃', first_strike=True)
def crimson_scale(engine, skill):
    engine.heal_player(round(engine.player.max_hp * 0.08 + engine.player.max_energy * 0.1, 2), '赤鳞复燃')
    bonus = round(engine.player.attack * 0.12, 2)
    engine.apply_buff_effect(engine.player, {'name': '赤鳞复燃·终伤', 'stat': 'final_damage', 'amount': 12}, 5)
    engine.apply_buff_effect(engine.player, {'name': '赤鳞复燃·附伤', 'stat': 'bonus_flat', 'amount': bonus}, 5)
    engine.log.append(f"赤鳞复燃！最终伤害+12%，普攻附{round(bonus)}伤害（5回合）")
    return True


@register_active('踏罡裁影', first_strike=True)
def step_shadow(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.1 + engine.player.agility * 0.7)
    engine.apply_buff_effect(engine.player, {'name': '踏罡裁影·必中', 'stat': 'sure_hit', 'amount': 0}, 2)
    engine.log.append(f"踏罡裁影！造成 {round(dmg)} 点伤害，必中2回合")
    return True


@register_active('追猎', first_strike=True)
def pursuit(engine, skill):
    bonus = round(engine.player.agility * 0.2, 2)
    engine.apply_buff_effect(engine.player, {'name': '追猎·附伤', 'stat': 'bonus_flat', 'amount': bonus}, 5)
    for i in range(5):
        if engine.monster.hp <= 0:
            break
        dmg = engine.hit_monster_normal(engine.player.attack * 0.25 + engine.player.max_energy * 0.1)
        engine.log.append(f"追猎 连击{i + 1}：{round(dmg)} 伤害")
    engine.log.append(f"追猎！获得{round(bonus)}附伤（5回合）")
    return True


@register_active('霜之哀伤', first_strike=True)
def frostmourne(engine, skill):
    engine.apply_buff_effect(engine.monster, {'name': '霜之哀伤·防御', 'stat': 'defense_percent', 'amount': -20}, 10, is_debuff=True)
    engine.apply_buff_effect(engine.monster, {'name': '霜之哀伤·敏捷', 'stat': 'agility_percent', 'amount': -20}, 10, is_debuff=True)
    dmg = round(engine.player.energy * 0.5, 2)
    engine.hit_monster_true(dmg)
    engine.log.append(f"霜之哀伤！敌方防御/敏捷-20%（10回合），造成{round(dmg)}伤害")
    return True


@register_active('风暴穿刺', first_strike=True)
def storm_pierce(engine, skill):
    dmg = engine.hit_monster_normal(
        engine.player.attack * 1.25 + engine.player.agility * 0.65 + engine.player.pen * 0.7 + engine.player.max_energy * 0.3)
    engine.log.append(f"风暴穿刺！造成 {round(dmg)} 点伤害")
    return True


@register_active('魔王斩', first_strike=True)
def demon_slash(engine, skill):
    dmg = engine.hit_monster_normal(engine.player.attack * 1.2 + engine.player.pen)
    engine.log.append(f"魔王斩！造成 {round(dmg)} 点伤害")
    return True


@register_active('黄昏禁锢', first_strike=True)
def dusk_prison(engine, skill):
    engine.apply_buff_effect(engine.monster, {'name': '黄昏禁锢·眩晕', 'stat': 'stun', 'amount': 0}, 3, is_debuff=True)
    engine.apply_buff_effect(engine.monster, {'name': '黄昏禁锢·易伤', 'stat': 'vuln', 'amount': 15}, 3, is_debuff=True)
    engine.log.append("黄昏禁锢！眩晕3回合，期间受伤害+15%")
    return True


# ================= 被动技能（战斗开始） =================
@register_passive('守护', on='battle_start')
def passive_guardian(engine, event):
    engine.apply_buff_effect(engine.player, {'name': '守护', 'stat': 'damage_reduce_percent', 'amount': 5}, -1)
    engine.log.append("守护生效：最终受伤-5%")


@register_passive('看破', on='battle_start')
def passive_insight(engine, event):
    engine.apply_buff_effect(engine.player, {'name': '看破·暴击', 'stat': 'crit', 'amount': 5}, -1)
    engine.apply_buff_effect(engine.player, {'name': '看破·穿透', 'stat': 'pen', 'amount': 5}, -1)
    engine.log.append("看破生效：暴击+5%，穿透+5%")


@register_passive('光阴之力', on='battle_start')
def passive_time_force(engine, event):
    engine.apply_buff_effect(engine.player, {'name': '光阴之力·攻击', 'stat': 'attack', 'amount': 15}, -1)
    engine.apply_buff_effect(engine.player, {'name': '光阴之力·穿透', 'stat': 'pen', 'amount': 15}, -1)
    engine.apply_buff_effect(engine.player, {'name': '光阴之力·敏捷', 'stat': 'agility', 'amount': 15}, -1)
    engine.log.append("光阴之力生效：攻击/穿透/敏捷+15")


@register_passive('神风', on='battle_start')
def passive_god_wind(engine, event):
    engine.apply_buff_effect(engine.player, {'name': '神风', 'stat': 'agility_percent', 'amount': 10}, -1)
    engine.log.append("神风生效：敏捷+10%")


@register_passive('自然之力', on='battle_start')
def passive_nature(engine, event):
    engine.player.max_hp = round(engine.player.max_hp * 1.05, 2)
    engine.player.max_energy = round(engine.player.max_energy * 1.05, 2)
    engine.log.append("自然之力生效：最大生命/能量+5%")


@register_passive('封灵诀', on='battle_start')
def passive_seal(engine, event):
    p = engine.player
    energy_loss = round(p.max_energy * 0.1, 2)
    p.max_energy = round(p.max_energy - energy_loss, 2)
    engine.apply_buff_effect(p, {'name': '封灵诀', 'stat': 'agility', 'amount': energy_loss}, -1)
    engine.log.append(f"封灵诀生效：能量上限-{round(energy_loss)}，敏捷+{round(energy_loss)}")


@register_passive('岩核蓄热', on='battle_start')
def passive_lava(engine, event):
    p = engine.player
    a = round(p.max_energy * 0.03, 2)
    b = round(4 + p.max_energy * 0.005, 2)
    engine.apply_buff_effect(p, {'name': '岩核蓄热·攻击', 'stat': 'attack', 'amount': a}, -1)
    engine.apply_buff_effect(p, {'name': '岩核蓄热·穿透', 'stat': 'pen', 'amount': b}, -1)
    engine.log.append(f"岩核蓄热生效：攻击+{round(a)}，穿透+{round(b)}")


@register_passive('渴血追袭', on=['battle_start', 'turn_start'])
def passive_bloodlust(engine, event):
    p = engine.player
    if event.name == 'battle_start':
        a = round(p.max_energy * 0.05, 2)
        engine.apply_buff_effect(p, {'name': '渴血追袭', 'stat': 'attack', 'amount': a}, -1)
        engine.log.append(f"渴血追袭生效：攻击+{round(a)}")
    elif event.name == 'turn_start':
        heal = round(0.02 * (p.attack + p.agility - p.defense), 2)
        if heal > 0:
            p.hp = min(p.max_hp, round(p.hp + heal, 2))
            engine.log.append(f"渴血追袭恢复 {round(heal)} 点生命")


@register_passive('燃魂之血', on='battle_start')
def passive_burn_soul(engine, event):
    p = engine.player
    hp_loss = round(p.max_hp * (p.max_energy * 0.0002), 2)
    p.max_hp = max(1, round(p.max_hp - hp_loss, 2))
    bonus = round(p.max_hp * p.max_energy * 0.00014, 2)
    engine.apply_buff_effect(p, {'name': '燃魂之血·攻击', 'stat': 'attack', 'amount': bonus}, -1)
    engine.apply_buff_effect(p, {'name': '燃魂之血·暴击', 'stat': 'crit', 'amount': bonus}, -1)
    engine.log.append(f"燃魂之血生效：最大生命-{round(hp_loss)}，攻击/暴击+{round(bonus)}")


@register_passive('统御者', on='battle_start')
def passive_overlord(engine, event):
    engine.apply_buff_effect(engine.player, {'name': '统御者', 'stat': 'final_damage', 'amount': 10}, -1)
    engine.log.append("统御者生效：最终伤害+10%")


@register_passive('低语回响', on='battle_start')
def passive_whisper(engine, event):
    p = engine.player
    v = round(p.max_energy * 0.02 + engine._get_gear_level('护甲') + engine._get_gear_level('饰品'), 2)
    engine.apply_buff_effect(p, {'name': '低语回响', 'stat': 'bonus_true', 'amount': v}, -1)
    engine.log.append(f"低语回响生效：普攻附{round(v)}真实伤害")


@register_passive('磐石', on='battle_start')
def passive_bedrock(engine, event):
    engine.apply_buff_effect(engine.player, {'name': '磐石', 'stat': 'block', 'amount': 20}, -1)
    engine.log.append("磐石生效：格挡+20")


@register_passive('岩火守望', on=['battle_start', 'turn_start'])
def passive_lava_watch(engine, event):
    p = engine.player
    if event.name == 'battle_start':
        v = round(engine._get_gear_level('头盔') + p.max_energy * 0.04, 2)
        engine.apply_buff_effect(p, {'name': '岩火守望', 'stat': 'block', 'amount': v}, 5)
        engine.log.append(f"岩火守望生效：格挡+{round(v)}（5回合）")
    elif event.name == 'turn_start':
        if engine.turn_count == 6:
            engine.apply_buff_effect(p, {'name': '岩火守望·暴击', 'stat': 'crit_percent', 'amount': 5}, -1)
            engine.log.append("岩火守望：第6回合暴击+5%")


@register_passive('王风号令', on='battle_start')
def passive_royal_wind(engine, event):
    p = engine.player
    engine.apply_buff_effect(p, {'name': '王风号令', 'stat': 'agility_percent', 'amount': round(p.max_energy * 0.012, 2)}, -1)
    engine.apply_buff_effect(p, {'name': '王风号令·必中', 'stat': 'sure_hit', 'amount': 0}, 1)
    engine.log.append("王风号令生效：敏捷+，第1回合必中")


@register_passive('狩猎形态', on='battle_start')
def passive_hunt_form(engine, event):
    p = engine.player
    engine.apply_buff_effect(p, {'name': '狩猎形态', 'stat': 'agility_percent', 'amount': round(6 + p.max_energy * 0.01, 2)}, 1)
    engine.apply_buff_effect(p, {'name': '狩猎形态·必中', 'stat': 'sure_hit', 'amount': 0}, 1)
    engine.log.append("狩猎形态生效：敏捷+，第1回合必中")


@register_passive('轮衡步', on='battle_start')
def passive_wheel_step(engine, event):
    p = engine.player
    engine.apply_buff_effect(p, {'name': '轮衡步', 'stat': 'agility_percent', 'amount': round(p.max_energy * 0.015, 2)}, -1)
    engine.apply_buff_effect(p, {'name': '轮衡步·必中', 'stat': 'sure_hit', 'amount': 0}, 1)
    engine.log.append("轮衡步生效：敏捷+，第1回合必中")


@register_passive('骇光猎印', on=['battle_start', 'turn_start'])
def passive_dread_hunt(engine, event):
    p = engine.player
    if event.name == 'battle_start':
        v = round(3 + p.max_energy * 0.006, 2)
        engine.apply_buff_effect(p, {'name': '骇光猎印', 'stat': 'crit', 'amount': v}, -1)
        engine.log.append(f"骇光猎印生效：暴击+{round(v)}")
    elif event.name == 'turn_start':
        if engine.turn_count == 3:
            v = round(8 + p.max_energy * 0.01, 2)
            engine.apply_buff_effect(p, {'name': '骇光猎印·终伤', 'stat': 'final_damage', 'amount': v}, 2)
            engine.log.append(f"骇光猎印：第3回合最终伤害+{v:.2f}%（2回合）")


@register_passive('祥云消难', on='battle_start')
def passive_auspicious_cloud(engine, event):
    p = engine.player
    v = round(p.max_energy * 0.03, 2)
    engine.apply_buff_effect(p, {'name': '祥云消难', 'stat': 'damage_reduce_percent', 'amount': v}, 3)
    engine.log.append(f"祥云消难生效：最终受伤-{v:.2f}%（3回合）")


# ================= 被动技能（每回合） =================
@register_passive('亚龙威仪', on='turn_start')
def passive_wyrm(engine, event):
    if engine.turn_count == 1:
        p = engine.player
        v = round(p.attack * 0.5, 2)
        engine.apply_buff_effect(p, {'name': '亚龙威仪', 'stat': 'attack', 'amount': v}, 1)
        engine.log.append(f"亚龙威仪生效：攻击+{round(v)}")


@register_passive('仲裁', on='turn_start')
def passive_arbitration(engine, event):
    if engine.turn_count >= 3:
        v = round(engine.monster.defense * 0.15, 2)
        engine.apply_buff_effect(engine.monster, {'name': '仲裁', 'stat': 'defense', 'amount': -v}, 1, is_debuff=True)
        engine.log.append(f"仲裁生效：敌方防御-{round(v)}")


@register_passive('暴风扰动', on='turn_start')
def passive_storm_disturb(engine, event):
    p = engine.player
    v = round(5 + p.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.monster, {'name': '暴风扰动', 'stat': 'final_damage', 'amount': -v}, 1, is_debuff=True)
    engine.log.append(f"暴风扰动生效：敌方最终伤害-{v:.2f}%")


@register_passive('破碎碾压', on='turn_start')
def passive_crush(engine, event):
    if engine.turn_count >= 5:
        p = engine.player
        v1 = round(p.pen * (engine._get_gear_level('武器') + engine._get_gear_level('护甲')) / 100.0, 2)
        v2 = round(p.max_energy * 0.02, 2)
        engine.apply_buff_effect(p, {'name': '破碎碾压·穿透', 'stat': 'pen', 'amount': v1}, 3)
        engine.apply_buff_effect(p, {'name': '破碎碾压·终伤', 'stat': 'final_damage', 'amount': v2}, 3)
        engine.log.append(f"破碎碾压生效：穿透+{round(v1)}，最终伤害+{v2:.2f}%")


@register_passive('秘钥开环', on='turn_start')
def passive_key_unlock(engine, event):
    if engine.turn_count == 5:
        p = engine.player
        engine.apply_buff_effect(p, {'name': '秘钥开环', 'stat': 'final_damage', 'amount': 20}, 2)
        dmg = round(p.max_energy * 2.5, 2)
        engine.monster.hp = round(engine.monster.hp - dmg, 2)
        engine.player_damage_dealt_this_turn += dmg
        engine.log.append(f"秘钥开环！造成 {round(dmg)} 点伤害，最终伤害+20%（2回合）")


@register_passive('月华守衡', on='turn_start')
def passive_moon_balance(engine, event):
    p = engine.player
    v = round(5 + p.max_energy * 0.01, 2)
    if engine.monster.hp >= engine.monster.max_hp * 0.5:
        engine.apply_buff_effect(p, {'name': '月华守衡·减伤', 'stat': 'damage_reduce_percent', 'amount': v}, 1)
    else:
        engine.apply_buff_effect(p, {'name': '月华守衡·敏捷', 'stat': 'agility_percent', 'amount': v}, 1)


@register_passive('亡者均衡', on='turn_start')
def passive_dead_balance(engine, event):
    p = engine.player
    v = round(3 + p.max_energy * 0.01, 2)
    if engine.monster.hp >= engine.monster.max_hp * 0.5:
        engine.apply_buff_effect(p, {'name': '亡者均衡·减伤', 'stat': 'damage_reduce_percent', 'amount': v}, 1)
    else:
        engine.apply_buff_effect(p, {'name': '亡者均衡·增伤', 'stat': 'final_damage', 'amount': v}, 1)


@register_passive('生死均势', on='turn_start')
def passive_life_death(engine, event):
    p = engine.player
    if engine.monster.hp >= engine.monster.max_hp * 0.5:
        engine.apply_buff_effect(p, {'name': '生死均势·减伤', 'stat': 'damage_reduce_percent', 'amount': 10}, 1)
    else:
        engine.apply_buff_effect(p, {'name': '生死均势·增伤', 'stat': 'final_damage', 'amount': 10}, 1)


@register_passive('镇压', on='turn_start')
def passive_suppress(engine, event):
    p = engine.player
    if engine.monster.hp < engine.monster.max_hp * 0.5:
        engine.apply_buff_effect(p, {'name': '镇压·增伤', 'stat': 'final_damage', 'amount': 15}, 1)
    else:
        engine.apply_buff_effect(p, {'name': '镇压·减伤', 'stat': 'damage_reduce_percent', 'amount': 15}, 1)
