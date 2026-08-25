# -*- coding: utf-8 -*-
"""战斗事件与同步事件总线。

事件在战斗引擎的固定节点派发，技能/被动通过订阅事件来实现效果。
所有事件均为同步派发：``emit`` 按注册顺序立即调用监听器。
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


class BattleEvent:
    """事件基类。子类通过 ``name`` 类属性标识事件名。"""
    name: str = "event"

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"


@dataclass
class BattleStart(BattleEvent):
    name = "battle_start"


@dataclass
class BattleEnd(BattleEvent):
    name = "battle_end"
    result: str = ""  # win / lose / escape


@dataclass
class TurnStart(BattleEvent):
    name = "turn_start"
    turn: int = 0


@dataclass
class TurnEnd(BattleEvent):
    name = "turn_end"
    turn: int = 0


@dataclass
class DamageEvent(BattleEvent):
    name = "damage_dealt"
    source: Any = None      # 攻击者
    target: Any = None      # 受击者
    amount: float = 0.0     # 最终结算伤害
    kind: str = "normal"    # DamageKind
    skill: Any = None       # 来源技能（可为 None）


@dataclass
class HealEvent(BattleEvent):
    name = "heal"
    target: Any = None
    amount: float = 0.0
    label: str = ""


@dataclass
class BuffAppliedEvent(BattleEvent):
    name = "buff_applied"
    target: Any = None
    buff: Any = None


@dataclass
class BuffRemovedEvent(BattleEvent):
    name = "buff_removed"
    target: Any = None
    buff: Any = None


class EventBus:
    """同步事件总线。"""

    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[BattleEvent], None]]] = {}

    def on(self, event_name: str, callback: Callable[[BattleEvent], None]):
        """注册监听器，返回原回调以便复用。"""
        self._listeners.setdefault(event_name, []).append(callback)
        return callback

    def off(self, event_name: str, callback: Callable[[BattleEvent], None]) -> None:
        listeners = self._listeners.get(event_name)
        if listeners and callback in listeners:
            listeners.remove(callback)

    def emit(self, event: BattleEvent) -> None:
        for callback in list(self._listeners.get(event.name, [])):
            callback(event)
