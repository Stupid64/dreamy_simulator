# -*- coding: utf-8 -*-
"""Buff 管理：应用、移除、百分比属性转换。

百分比 stat（attack_percent 等）在应用时基于目标当前属性折算为绝对值，
再以绝对值 buff 存储，与历史行为保持一致。
"""
from models.buff import Buff


class BuffManager:
    # 百分比 stat -> 对应的绝对值属性
    PERCENT_STATS = {
        'attack_percent': 'attack',
        'defense_percent': 'defense',
        'agility_percent': 'agility',
        'crit_percent': 'crit',
    }
    # 直接作用于角色属性的 stat
    ATTR_STATS = ('defense', 'crit', 'agility', 'attack', 'pen')

    def __init__(self, engine) -> None:
        self.engine = engine

    def apply(self, target, effect, duration, is_debuff=False,
              start_next_turn=False):
        """应用一个效果（dict），返回创建的 Buff（无效果时返回 None）。"""
        if not effect:
            return None

        stat = effect.get('stat')
        amount = float(effect.get('amount', 0))
        buff_name = effect.get('name', '效果')

        # 百分比属性按当前值折算为绝对值
        if stat in self.PERCENT_STATS:
            base_attr = self.PERCENT_STATS[stat]
            actual_amount = round(getattr(target, base_attr) * amount / 100.0)
            stat = base_attr
        else:
            actual_amount = amount

        buff = Buff(buff_name, stat, actual_amount, duration, is_debuff)
        if start_next_turn:
            buff.created_turn = self.engine.turn_count

        target.buffs.append(buff)
        self._apply_stat(target, stat, actual_amount)
        return buff

    def remove(self, target, buff) -> None:
        """移除 buff 并回退其属性影响。"""
        if buff.stat in self.ATTR_STATS:
            setattr(target, buff.stat,
                    round(getattr(target, buff.stat) - buff.amount, 2))
        target.buffs.remove(buff)

    @staticmethod
    def _apply_stat(target, stat, amount) -> None:
        if stat in BuffManager.ATTR_STATS:
            setattr(target, stat, round(getattr(target, stat) + amount, 2))

    # ---------- 查询 ----------
    def total(self, character, stat) -> float:
        """汇总角色身上指定 stat 的所有 buff 数值。"""
        total = 0.0
        for buff in character.buffs:
            if buff.stat == stat:
                total += buff.amount
        return total

    def has(self, character, stat) -> bool:
        return any(buff.stat == stat for buff in character.buffs)

    def has_named(self, character, name) -> bool:
        return any(buff.name == name for buff in character.buffs)

    def tick(self, character, turn_count):
        """推进 buff 倒计时，返回过期 buff 列表。

        规则：施放当回合（created_turn == turn_count）不递减，
        持续回合从下一回合开始倒计时。
        """
        expired = []
        for buff in character.buffs:
            if buff.created_turn == turn_count:
                continue
            if buff.tick():
                expired.append(buff)
        return expired
