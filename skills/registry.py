# -*- coding: utf-8 -*-
"""技能注册表。

- 主动技能：``register_active(name)`` 注册执行器 ``handler(engine, skill)``。
- 被动技能：``register_passive(name, on)`` 注册事件监听 ``handler(engine, event)``，
  ``on`` 为事件名或事件名列表。

新增技能只需在此注册，无需改动战斗引擎与界面分支逻辑。
"""
from typing import Callable, Dict, List, Tuple

# name -> handler(engine, skill)
ACTIVE_HANDLERS: Dict[str, Callable] = {}

# list[(event_name, skill_name, handler(engine, event))]
PASSIVE_LISTENERS: List[Tuple[str, str, Callable]] = []

# 玩家先手技能（无视敏捷先后手）
FIRST_STRIKE_SKILLS = set()


def register_active(name: str, first_strike: bool = False):
    """注册主动技能执行器。

    first_strike=True 表示该技能无视敏捷先后手，玩家必定先出手。
    """
    def decorator(fn: Callable) -> Callable:
        ACTIVE_HANDLERS[name] = fn
        if first_strike:
            FIRST_STRIKE_SKILLS.add(name)
        return fn
    return decorator


def register_passive(name: str, on):
    """注册被动技能事件监听。``on`` 为事件名或事件名列表。"""
    events = [on] if isinstance(on, str) else list(on)

    def decorator(fn: Callable) -> Callable:
        for event_name in events:
            PASSIVE_LISTENERS.append((event_name, name, fn))
        return fn
    return decorator


def get_active_handler(name: str):
    return ACTIVE_HANDLERS.get(name)


def get_passive_listeners(name: str) -> List[Tuple[str, Callable]]:
    """返回指定技能的所有 (事件名, 监听器)。"""
    return [(ev, fn) for ev, n, fn in PASSIVE_LISTENERS if n == name]
