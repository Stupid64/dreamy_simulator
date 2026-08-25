# -*- coding: utf-8 -*-
"""伤害结算管道。

统一实现伤害计算，按固定顺序应用各阶段：
基础伤害(攻击×倍率×浮动×暴击) → 防御减免(仅普通伤害) →
受击方乘算修正(怪物防御反击/光暗减伤) → 攻击方乘算修正(黄昏增伤) →
最终伤害加成 → 最终受伤减免 → 易伤 → 绝对防御 → 破穿棘刺 →
固定减伤(格挡/永恒减伤) → 保底取整。

真实伤害不走管道，直接返回数值。
"""
from models.enums import DamageKind


class DamageCalculator:
    """依赖引擎提供状态与日志的伤害计算器。"""

    def __init__(self, engine) -> None:
        self.engine = engine

    @property
    def log(self):
        return self.engine.log

    # ---------- 基础 ----------
    def get_attack(self, attacker):
        """攻击基础值，按需施加浮动（90%~110%）。"""
        base = attacker.attack
        if self.engine.attack_variance:
            return base * self.engine.rng.uniform(0.9, 1.1)
        return base

    def _crit_multiplier(self, attacker):
        """暴击倍率。暴击率 = crit%100/100，等级提供 0.2×level 基础倍率。"""
        crit_stat = attacker.crit
        crit_level = int(crit_stat) // 100
        crit_chance = (crit_stat % 100) / 100.0
        occurred = self.engine.rng.random() < crit_chance
        multiplier = 1.0 + 0.2 * crit_level
        if occurred:
            multiplier += 0.2
            self.log.append("暴击！")
        return multiplier

    # ---------- 结算 ----------
    def calculate(self, attacker, defender, skill_power=1.0,
                  kind=DamageKind.NORMAL) -> float:
        """计算一次伤害（不修改血量）。"""
        if kind == DamageKind.TRUE:
            return round(skill_power, 2)

        e = self.engine
        damage = self.get_attack(attacker) * skill_power
        damage *= self._crit_multiplier(attacker)

        # 防御减免（仅普通伤害）
        effective_def = max(0, defender.defense - getattr(attacker, 'pen', 0))
        damage *= 1.0 / (1.0 + 0.01 * effective_def)

        # 怪物防御反击：受到伤害减半
        if defender is e.monster and e.has_buff_named(defender, '防御反击'):
            damage *= 0.5
            self.log.append("怪物处于防御反击状态，伤害减半！")

        # 光暗减伤：受到伤害 -30%
        if defender is e.player and e.has_buff_named(defender, '光暗减伤'):
            damage = round(damage * 0.7, 2)
            self.log.append("光暗减伤生效，伤害减少30%")

        # 黄昏增伤：造成伤害 +10%
        if attacker is e.player and e.has_buff_named(attacker, '黄昏增伤'):
            damage = round(damage * 1.1, 2)
            self.log.append("黄昏增伤生效，伤害+10%")

        # 最终伤害加成（攻击方）
        final_damage = e.buff_total(attacker, 'final_damage')
        if final_damage:
            damage = round(damage * (1 + final_damage / 100.0), 2)
            self.log.append(f"最终伤害提升生效，伤害+{final_damage:.2f}%")

        # 最终受伤减免（防御方）
        reduce_pct = e.buff_total(defender, 'damage_reduce_percent')
        if reduce_pct:
            damage = round(damage * (1 - reduce_pct / 100.0), 2)
            self.log.append(f"最终受伤减免生效，伤害-{reduce_pct:.2f}%")

        # 易伤（防御方）
        vuln = e.buff_total(defender, 'vuln')
        if vuln:
            damage = round(damage * (1 + vuln / 100.0), 2)
            self.log.append(f"易伤生效，伤害+{vuln:.2f}%")

        # 绝对防御：玩家受击 -5%
        if defender is e.player and e.ji_yu_passive:
            damage = round(damage * 0.95, 2)
            self.log.append("绝对防御生效，伤害-5%")

        # 破穿棘刺：怪物受伤 +10%
        if defender is e.monster and e.has_buff_named(defender, '破穿棘刺'):
            damage = round(damage * 1.1, 2)
            self.log.append("破穿棘刺：敌方受伤+10%")

        # 格挡：固定减伤
        block = e.buff_total(defender, 'block')
        if block:
            damage = max(1, round(damage - block, 2))
            self.log.append(f"格挡生效，伤害减少 {round(block)} 点")

        # 永恒减伤：固定减伤（仅玩家）
        if defender is e.player:
            red = e.eternal_reduction()
            if red > 0:
                damage = max(1, round(damage - red, 2))
                self.log.append(f"永恒减伤生效，伤害减少 {round(red)} 点")

        return round(damage, 2)
