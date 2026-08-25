# -*- coding: utf-8 -*-
"""基础技能：攻击、防御反击、治疗、怒击、三连击、旋风斩、坚守、狂暴之力。"""
from engine.events import HealEvent
from skills.registry import register_active


@register_active('攻击')
def skill_attack(engine, skill):
    engine.perform_attack(engine.player, engine.monster, skill)
    return True


@register_active('防御反击')
def skill_defend(engine, skill):
    engine.log.append("你使用了防御反击，进入防御反击状态")
    engine.defend_counter = True
    return True


@register_active('治疗')
def skill_heal(engine, skill):
    amount = round(engine.player.max_hp * 0.25, 2)
    if engine.monster.world_boss:
        amount = round(amount * 0.7, 2)
        engine.log.append("世界Boss压制，治疗量降低30%")
    engine.player.hp = min(engine.player.max_hp, round(engine.player.hp + amount, 2))
    engine.log.append(f"你使用了治疗，恢复 {round(amount)} 点生命")
    engine.bus.emit(HealEvent(target=engine.player, amount=amount, label='治疗'))
    return True


@register_active('怒击')
def skill_rage_strike(engine, skill):
    engine.perform_attack(engine.player, engine.monster, skill)
    return True


@register_active('三连击')
def skill_triple_strike(engine, skill):
    for i in range(3):
        if engine.monster.hp <= 0:
            break
        engine.log.append(f"三连击 第{i + 1}击")
        engine.perform_attack(engine.player, engine.monster, power_multiplier=0.5)
    return True


@register_active('旋风斩')
def skill_whirlwind(engine, skill):
    engine.perform_attack(engine.player, engine.monster, skill)
    return True


@register_active('坚守')
def skill_hold(engine, skill):
    engine.log.append("坚守！防御提升10%，持续10回合")
    engine.apply_buff_effect(engine.player, skill.buff_effect, skill.duration,
                             start_next_turn=True)
    return True


@register_active('狂暴之力')
def skill_berserk(engine, skill):
    engine.log.append("狂暴之力！攻击力提升20%，持续6回合")
    engine.apply_buff_effect(engine.player, skill.buff_effect, skill.duration,
                             start_next_turn=True)
    return True
