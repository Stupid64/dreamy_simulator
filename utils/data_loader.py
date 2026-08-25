import pandas as pd
import json
import re
from config import EXCEL_FILE


def safe_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def load_monsters():
    df = pd.read_excel(EXCEL_FILE, sheet_name='monsters')
    monsters = []
    from models.monster import Monster

    # 存储副本ID与名称的映射
    dungeon_dict = {}

    for idx, row in df.iterrows():
        dungeon_cell = str(row['副本次序']).strip()
        dungeon_id = 0
        dungeon_name = ""
        world_boss = False

        # 世界BOSS（副本次序含"世界boss"）
        if '世界boss' in dungeon_cell.lower():
            world_boss = True
            dungeon_id = -1
            dungeon_name = "世界BOSS"
        else:
            # 解析副本序号与名称：例如 "1异变丛林" 或 "2"
            match = re.match(r'^(\d+)(.*)$', dungeon_cell)
            if match:
                dungeon_id = int(match.group(1))
                name_part = match.group(2).strip()
                if name_part:
                    dungeon_name = name_part
                    dungeon_dict[dungeon_id] = dungeon_name
                else:
                    dungeon_name = dungeon_dict.get(dungeon_id, "未知副本")
            else:
                try:
                    dungeon_id = int(float(dungeon_cell))
                    dungeon_name = dungeon_dict.get(dungeon_id, "未知副本")
                except:
                    dungeon_id = 0
                    dungeon_name = "未知副本"

        # 怪物ID使用行号（从1开始）
        monster_id = idx + 1

        m = Monster(
            id=monster_id,
            name=str(row['名称']),
            type=str(row['类型']),
            attack=safe_int(row['攻击']),
            defense=safe_int(row['防御']),
            hp=safe_int(row['生命']),
            agility=safe_int(row['敏捷']),
            skill_pool=[s.strip() for s in str(row.get('技能池', '')).split(',') if s.strip()],
            gold=safe_int(row.get('金币', 0)),
            exp=safe_int(row.get('经验', 0)),
            defend_chance=safe_float(row.get('防御概率', 0.1)),
            dungeon_id=dungeon_id,
            dungeon_name=dungeon_name,
            world_boss=world_boss
        )
        monsters.append(m)
    return monsters


def load_equipments():
    df = pd.read_excel(EXCEL_FILE, sheet_name='equipments')
    equipments = []
    from models.equipment import Equipment
    for _, row in df.iterrows():
        eq = Equipment(
            id=safe_int(row['编号']),
            name=str(row['名称']),
            slot=str(row['部位']),
            price=safe_int(row.get('基础价格', 0)),
            attack=safe_int(row.get('攻击', 0)),
            defense=safe_int(row.get('防御', 0)),
            hp=safe_int(row.get('生命', 0)),
            energy=safe_int(row.get('能量', 0)),
            crit=safe_int(row.get('暴击', 0)),
            pen=safe_int(row.get('穿透', 0)),
            agility=safe_int(row.get('敏捷', 0))
        )
        equipments.append(eq)
    return equipments


def load_skills():
    df = pd.read_excel(EXCEL_FILE, sheet_name='skills')
    skills = []
    from models.skill import Skill
    for _, row in df.iterrows():
        buff_raw = row.get('Buff效果')
        if isinstance(buff_raw, str):
            try:
                buff_raw = json.loads(buff_raw)
            except:
                buff_raw = None
        s = Skill(
            id=safe_int(row['编号']),
            name=str(row['名称']),
            type=str(row['类型']),
            power=safe_float(row['威力'], 1.0),
            energy_cost=safe_int(row['能量消耗']),
            buff_effect=buff_raw,
            duration=safe_int(row['持续回合']),
            target=str(row['目标']),
            desc=str(row['描述']),
            cooldown=safe_int(row.get('冷却', 0))
        )
        skills.append(s)
    return skills