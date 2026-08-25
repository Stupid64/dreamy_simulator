# -*- coding: utf-8 -*-
"""已有装备技能（技能ID -1 ~ -19）。

主动技能均为玩家先手（无视敏捷先后手）；被动技能通过事件监听实现。
"""
from skills.registry import register_active, register_passive


# ================= 主动技能 =================
@register_active('风暴降临', first_strike=True)
def storm_descend(engine, skill):
    engine.apply_buff_effect(engine.player,
                             {'name': '风暴降临', 'stat': 'none', 'amount': 0},
                             50, start_next_turn=True)
    engine.log.append("风暴降临！每次攻击附加真实伤害，持续50回合")
    return True


@register_active('光暗侵蚀', first_strike=True)
def light_dark(engine, skill):
    effective_def = max(0, engine.monster.defense - engine.player.pen)
    raw_dmg = (engine.player.attack * 1.5 + engine.player.max_energy * 2) / (1 + 0.01 * effective_def)
    dmg = engine.apply_sunset(round(raw_dmg, 2))
    engine.monster.hp = round(engine.monster.hp - dmg, 2)
    engine.player_damage_dealt_this_turn += dmg
    engine.log.append(f"光暗侵蚀！对 {engine.monster.name} 造成 {round(dmg)} 点伤害（无法格挡/闪避）")
    engine.apply_buff_effect(engine.player,
                             {'name': '光暗减伤', 'stat': 'none', 'amount': 0},
                             4, start_next_turn=True)
    engine.log.append("光暗减伤！受到的伤害减少30%，持续4回合")
    return True


@register_active('噬浪突袭', first_strike=True)
def scale_rush(engine, skill):
    effective_def = max(0, engine.monster.defense - engine.player.pen)
    base_power = engine.player.attack + engine.player.max_energy * 2
    crit_factor = 1 + 0.002 * engine.player.crit
    raw_dmg = base_power * crit_factor / (1 + 0.01 * effective_def)
    dmg = engine.apply_sunset(round(raw_dmg, 2))
    engine.monster.hp = round(engine.monster.hp - dmg, 2)
    engine.player_damage_dealt_this_turn += dmg
    engine.log.append(f"噬浪突袭！对 {engine.monster.name} 造成 {round(dmg)} 点伤害")
    engine.apply_buff_effect(engine.player, skill.buff_effect, skill.duration,
                             start_next_turn=True)
    engine.log.append("噬浪疾步！敏捷提升5%，持续2回合")
    return True


@register_active('冥域', first_strike=True)
def nether_realm(engine, skill):
    amount = round(engine.player.max_energy * 0.1, 2)
    engine.apply_buff_effect(engine.monster, {'name': '冥域·攻击降低', 'stat': 'attack', 'amount': -amount},
                             30, is_debuff=True, start_next_turn=True)
    engine.apply_buff_effect(engine.monster, {'name': '冥域·防御降低', 'stat': 'defense', 'amount': -amount},
                             30, is_debuff=True, start_next_turn=True)
    engine.apply_buff_effect(engine.monster, {'name': '冥域·敏捷降低', 'stat': 'agility', 'amount': -amount},
                             30, is_debuff=True, start_next_turn=True)
    engine.log.append(f"冥域降临！敌方攻击/防御/敏捷降低 {round(amount)} 点，持续30回合")
    return True


@register_active('赐剑长驱', first_strike=True)
def bestow_sword(engine, skill):
    atk_bonus = round(engine.player.max_energy * 0.5, 2)
    engine.apply_buff_effect(engine.player, {'name': '赐剑长驱', 'stat': 'attack', 'amount': atk_bonus},
                             5, start_next_turn=True)
    engine.log.append(f"赐剑长驱！攻击提高 {round(atk_bonus)} 点，持续5回合")
    return True


@register_active('破穿棘刺', first_strike=True)
def break_thorn(engine, skill):
    effective_def = max(0, engine.monster.defense - engine.player.pen)
    base_dmg = engine.player.attack + engine.player.max_energy * 0.4 + engine.player.pen * 0.2
    raw_dmg = round(base_dmg / (1 + 0.01 * effective_def), 2)
    true_dmg = engine.turn_count * 2
    total_dmg = raw_dmg + true_dmg
    engine.monster.hp = round(engine.monster.hp - total_dmg, 2)
    engine.player_damage_dealt_this_turn += total_dmg
    engine.log.append(f"破穿棘刺！造成 {round(raw_dmg)} 点伤害及 {true_dmg} 点真实伤害")
    engine.apply_buff_effect(engine.monster, {'name': '破穿棘刺', 'stat': 'none', 'amount': 0},
                             5, is_debuff=True, start_next_turn=True)
    engine.log.append("敌方最终受伤提高10%，持续5回合")
    return True


@register_active('轻盈之语', first_strike=True)
def light_words(engine, skill):
    heal_amount = round(engine.player.max_energy, 2)
    if engine.monster.world_boss:
        heal_amount = round(heal_amount * 0.7, 2)
        engine.log.append("世界Boss压制，治疗量降低30%")
    def_bonus = round(0.1 * engine.player.max_energy, 2)
    engine.player.hp = min(engine.player.max_hp, round(engine.player.hp + heal_amount, 2))
    engine.apply_buff_effect(engine.player, {'name': '轻盈之语', 'stat': 'defense', 'amount': def_bonus},
                             1, start_next_turn=True)
    engine.log.append(f"轻盈之语！恢复 {round(heal_amount)} 生命，防御提升 {round(def_bonus)} 点")
    return True


@register_active('幽幕暴动', first_strike=True)
def dark_riot(engine, skill):
    fd_pct = round(20 + engine.player.max_energy * 0.01, 2)
    agi_pct = round(25 + engine.player.max_energy * 0.01, 2)
    engine.apply_buff_effect(engine.player, {'name': '幽幕暴动·最终伤害', 'stat': 'final_damage', 'amount': fd_pct},
                             6, start_next_turn=True)
    engine.apply_buff_effect(engine.player, {'name': '幽幕暴动·敏捷', 'stat': 'agility_percent', 'amount': agi_pct},
                             6, start_next_turn=True)
    engine.log.append(f"幽幕暴动！最终伤害 +{fd_pct:.2f}%，敏捷 +{agi_pct:.2f}%，持续6回合")
    return True


@register_active('地脉冲爆', first_strike=True)
def earth_pulse(engine, skill):
    effective_def = max(0, engine.monster.defense - engine.player.pen)
    base_dmg = engine.player.attack + engine.player.defense
    raw_dmg = round(base_dmg / (1 + 0.01 * effective_def), 2)
    dmg = engine.apply_sunset(raw_dmg)
    agi_penalty = round(engine.player.max_energy * 0.2, 2)
    engine.monster.hp = round(engine.monster.hp - dmg, 2)
    engine.player_damage_dealt_this_turn += dmg
    engine.apply_buff_effect(engine.monster, {'name': '地脉冲爆', 'stat': 'agility', 'amount': -agi_penalty},
                             2, is_debuff=True, start_next_turn=True)
    engine.log.append(f"地脉冲爆！造成 {round(dmg)} 点伤害，敌方敏捷降低 {round(agi_penalty)} 点")
    return True


# ================= 被动技能 =================
@register_passive('悲恸光环', on='battle_start')
def sorrow_aura(engine, event):
    coeff = max(0.0, 1 - engine.player.max_energy * 0.0001)
    engine.monster.attack = round(engine.monster.attack * coeff, 2)
    engine.monster.defense = round(engine.monster.defense * coeff, 2)
    engine.monster.agility = round(engine.monster.agility * coeff, 2)
    engine.log.append(f"悲恸光环生效！敌人属性被削弱至 {coeff * 100:.2f}%")


@register_passive('黄昏时刻·永恒', on='battle_start')
def sunset_eternal(engine, event):
    weapon_lv = engine.player.get_weapon_level()
    reduction = round(weapon_lv * 1 + engine.player.max_energy * 0.01, 2)
    if reduction > 0:
        engine.apply_buff_effect(engine.player,
                                 {'name': '永恒减伤', 'stat': 'none', 'amount': reduction}, -1)
        engine.log.append(f"永恒枪盾：伤害减免 {round(reduction)} 点")


@register_passive('绝对防御', on='battle_start')
def absolute_defense(engine, event):
    engine.ji_yu_passive = True
    engine.log.append("绝对防御生效：最终受伤-5%")


@register_passive('长明无忧', on=['battle_start', 'turn_start'])
def eternal_peace(engine, event):
    if event.name == 'battle_start':
        engine.yin_mi_regen_amount = round(
            engine.player.max_hp * (0.005 + engine.player.max_energy * 0.00001), 2)
        engine.log.append("长明无忧生效：每回合恢复生命")
    elif event.name == 'turn_start':
        if engine.yin_mi_regen_amount > 0:
            engine.player.hp = min(engine.player.max_hp,
                                   round(engine.player.hp + engine.yin_mi_regen_amount, 2))
            engine.log.append(f"长明无忧恢复 {round(engine.yin_mi_regen_amount)} 点生命")


@register_passive('遮天蔽日', on=['battle_start', 'turn_start'])
def sky_cover(engine, event):
    if event.name == 'battle_start':
        engine.fu_tian_active = True
    elif event.name == 'turn_start':
        if engine.fu_tian_active and engine.turn_count <= 3:
            p = engine.player
            agi_penalty = round(engine.monster.agility * (p.max_energy * 0.03) / 100, 2)
            if agi_penalty > 0:
                engine.apply_buff_effect(engine.monster, {'name': '遮天蔽日·敏降', 'stat': 'agility', 'amount': -agi_penalty},
                                         1, is_debuff=True)
            crit_bonus = round(p.crit * (p.max_energy * 0.01) / 100, 2)
            def_bonus = round(p.defense * (p.max_energy * 0.02) / 100, 2)
            if crit_bonus > 0:
                engine.apply_buff_effect(p, {'name': '遮天蔽日·暴击提升', 'stat': 'crit', 'amount': crit_bonus}, 1)
            if def_bonus > 0:
                engine.apply_buff_effect(p, {'name': '遮天蔽日·防御提升', 'stat': 'defense', 'amount': def_bonus}, 1)
            engine.log.append("遮天蔽日生效！前三回合效果")


@register_passive('天命所归', on=['battle_start', 'turn_start'])
def destiny(engine, event):
    if event.name == 'battle_start':
        engine.zhen_ming_done = False
    elif event.name == 'turn_start':
        if not engine.zhen_ming_done and engine.turn_count == 5:
            dmg = round(0.4 * engine.player.max_energy, 2)
            engine.monster.hp = round(engine.monster.hp - dmg, 2)
            engine.player.hp = min(engine.player.max_hp, round(engine.player.hp + dmg, 2))
            engine.log.append(f"天命所归！对敌方造成 {round(dmg)} 点真实伤害，并恢复等额生命")
            engine.zhen_ming_done = True


@register_passive('黄昏时刻', on='turn_start')
def sunset_moment(engine, event):
    if engine.turn_count == 10 and not engine.sunset_triggered:
        engine.apply_buff_effect(engine.player, {'name': '黄昏增伤', 'stat': 'none', 'amount': 0}, -1)
        engine.log.append("黄昏时刻！获得10%最终伤害增幅（永久）")
        effective_def = max(0, engine.monster.defense - engine.player.pen)
        raw_dmg = engine.player.max_energy * 5 / (1 + 0.01 * effective_def)
        dmg = engine.apply_sunset(round(raw_dmg, 2))
        engine.monster.hp = round(engine.monster.hp - dmg, 2)
        engine.player_damage_dealt_this_turn += dmg
        engine.log.append(f"黄昏时刻冲击！对 {engine.monster.name} 造成 {round(dmg)} 点伤害")
        engine.sunset_triggered = True
