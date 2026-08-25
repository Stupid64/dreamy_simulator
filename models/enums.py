# -*- coding: utf-8 -*-
"""核心枚举定义：伤害类型、技能类型、目标类型等。

使用 ``str`` 混入，枚举值可直接与历史代码中的字符串比较，降低迁移成本。
"""
from enum import Enum


class DamageKind(str, Enum):
    """伤害类型。

    - NORMAL：普通伤害，受目标有效防御减免，参与攻击浮动与暴击。
    - TRUE：真实伤害，无视防御与百分比减伤，直接扣血。
    """
    NORMAL = "normal"
    TRUE = "true"


class SkillType(str, Enum):
    """技能类型。"""
    ACTIVE = "active"
    PASSIVE = "passive"
    BUFF = "buff"
    HEAL = "heal"


class TargetType(str, Enum):
    """技能目标。"""
    SELF = "self"
    ENEMY = "enemy"


class Stat(str, Enum):
    """可被 buff 影响的属性名（与历史代码字符串保持一致）。"""
    ATTACK = "attack"
    DEFENSE = "defense"
    HP = "hp"
    ENERGY = "energy"
    CRIT = "crit"
    PEN = "pen"
    AGILITY = "agility"

    # 百分比属性
    ATTACK_PERCENT = "attack_percent"
    DEFENSE_PERCENT = "defense_percent"
    AGILITY_PERCENT = "agility_percent"
    CRIT_PERCENT = "crit_percent"
    HP_PERCENT = "hp_percent"
    ENERGY_PERCENT = "energy_percent"
    PEN_PERCENT = "pen_percent"

    # 结算相关
    FINAL_DAMAGE = "final_damage"
    DAMAGE_REDUCE_PERCENT = "damage_reduce_percent"
    VULN = "vuln"
    BLOCK = "block"

    # 状态标记
    SURE_HIT = "sure_hit"
    SURE_DODGE = "sure_dodge"
    STUN = "stun"
    HEAL_REDUCE = "heal_reduce"
    REGEN = "regen"
    BONUS_FLAT = "bonus_flat"
    BONUS_TRUE = "bonus_true"
    NONE = "none"
