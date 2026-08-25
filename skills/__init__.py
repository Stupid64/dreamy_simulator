# -*- coding: utf-8 -*-
"""技能系统包。

导入本包即完成所有技能执行器与被动监听器的注册。
"""
from skills import registry, core, legacy_equipment, equipment  # noqa: F401
from skills.catalog import (  # noqa: F401
    LEGACY_SKILLS, build_skills, entry_desc, entry_buffs,
    unlocked_legacy_skills, skill_id_to_name, skill_name_to_id,
    legacy_entry_by_id, legacy_entry_by_name,
)