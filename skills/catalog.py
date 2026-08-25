# -*- coding: utf-8 -*-
"""技能目录：统一管理装备技能的元数据、装备解锁关系与动态数值。

- 已有装备技能（LEGACY_SKILLS）集中在此，界面展示、技能构建、方案存读均通过本模块。
- 新装备技能（utils.equipment_skills）保持数据驱动，由界面直接读取。
"""
from models.skill import Skill
from utils.equipment_skills import NEW_EQUIPMENT_SKILLS, EQUIPMENT_SKILL_MAP


# ================= 装备名称常量 =================
STORM_ARMOR_NAME = "隐秘-风暴降临之铠"
STORM_WEAPON_NAME = "极炎飓风斩"
CHAOS_ORB_NAME = "混沌宝珠"
LIGHT_DARK_WEAPON_NAME = "隐秘-光暗边界"
CROWN_NAME = "祭礼冠冕"
GREAVES_NAME = "哀悼胫甲"
RING_NAME = "悲鸣之环"
SUNSET_ARMOR_NAME = "永恒落日之铠"
SUNSET_WEAPON_NAME = "永恒枪盾"
SCALE_BOOTS_NAME = "隐秘-噬浪鳞靴"
WU_JIN_MING_YU = "无尽冥域"
WANG_MING_ZHAN_KAI = "王命号令战铠"
AN_YING_MO_MIAN = "暗影魔冕"
DI_TENG_JI_REN = "帝藤棘刃帷幔"
FU_TIAN_MO_CHAN = "覆天魔铲"
ZI_RAN_ZHI_JI = "自然之迹"
JI_YU_SHEN_JIA = "极御神甲"
ZHEN_MING_XUE_SHI = "真命血石"
YIN_MI_CHANG_MING = "隐秘-长明圣玉"
YOU_MU_BAO_DONG_PAO = "幽幕暴动袍"


# ================= 动态描述 / 数值 =================
def _divine_wind_buffs(p):      # 神风烈火
    return [{'stat': 'attack', 'amount': round(30 + 0.06 * p.max_energy)}]


def _divine_wind_desc(p):
    return f"攻击力提升 {round(30 + 0.06 * p.max_energy)} 点（基于最大能量）"


def _chaos_buffs(p):            # 混沌初开
    return [{'stat': 'defense', 'amount': round(p.max_energy * 0.001 * p.base_defense)}]


def _chaos_desc(p):
    return f"防御提升 {round(p.max_energy * 0.001 * p.base_defense)} 点（基于能量×防御力）"


def _sorrow_desc(p):
    coeff = max(0.0, 1 - p.max_energy * 0.0001)
    return f"敌人属性削弱至 {coeff * 100:.2f}%（基于能量）"


def _sunset_eternal_buffs(p):   # 黄昏时刻·永恒
    weapon_lv = p.get_weapon_level()
    return [{'stat': 'attack', 'amount': round(weapon_lv * 2 + p.max_energy * 0.02)}]


def _sunset_eternal_desc(p):
    weapon_lv = p.get_weapon_level()
    atk_bonus = round(weapon_lv * 2 + p.max_energy * 0.02)
    def_reduce = round(weapon_lv * 1 + p.max_energy * 0.01)
    return f"伤害减免 {def_reduce} 点，攻击力 +{atk_bonus} 点（基于武器强化与能量）"


def _nether_desc(p):
    amount = round(p.max_energy * 0.1)
    return f"消耗80能量，CD50回合，降低敌方攻击/防御/敏捷各 {amount} 点，持续30回合"


def _bestow_sword_buffs(p):     # 赐剑长驱
    return [{'stat': 'attack', 'amount': round(p.max_energy * 0.5)}]


def _bestow_sword_desc(p):
    return f"消耗50能量，CD8回合，攻击提高 {round(p.max_energy * 0.5)} 点，持续5回合"


def _dark_assault_buffs(p):     # 暗影狂袭
    pct = p.max_energy / 100.0
    return [{'stat': 'pen_percent', 'amount': pct},
            {'stat': 'agility_percent', 'amount': pct}]


def _dark_assault_desc(p):
    pct = p.max_energy / 100.0
    pen_bonus = round(p.base_pen * pct / 100.0)
    agi_bonus = round(p.base_agility * pct / 100.0)
    return f"被动：穿透 +{pen_bonus}，敏捷 +{agi_bonus}（基于能量 {pct:.2f}%）"


def _sky_cover_desc(p):
    agi_pen = p.max_energy * 0.03
    crit_bonus = p.max_energy * 0.01
    def_bonus = p.max_energy * 0.02
    return f"被动：前三回合敌方敏捷-{agi_pen:.2f}%，己方暴击+{crit_bonus:.2f}%，防御+{def_bonus:.2f}%"


def _light_words_desc(p):
    heal_amount = round(p.max_energy)
    def_bonus = round(0.1 * p.max_energy)
    return f"消耗70能量，CD10回合，恢复 {heal_amount} 生命，防御提升 {def_bonus} 点持续1回合"


def _earth_pulse_desc(p):
    agi_pen = round(p.max_energy * 0.2)
    base_dmg = round(p.attack + p.defense)
    return f"消耗80能量，CD10回合，基础伤害 {base_dmg} 点（受怪物防御减免），降低敌方敏捷 {agi_pen} 点持续2回合"


def _destiny_desc(p):
    dmg = round(0.4 * p.max_energy)
    return f"被动：第5回合对敌方造成 {dmg} 点真实伤害并等额回血"


def _eternal_peace_desc(p):
    regen_pct = 0.5 + p.max_energy * 0.001
    return f"被动：每回合恢复最大生命的 {regen_pct:.2f}%"


def _dark_riot_desc(p):
    fd_bonus = round(20 + p.max_energy * 0.01, 2)
    agi_bonus = round(25 + p.max_energy * 0.01, 2)
    return f"消耗30能量，CD18回合，最终伤害 +{fd_bonus:.2f}%，敏捷 +{agi_bonus:.2f}%，持续6回合"


# ================= 已有装备技能目录 =================
# requires：解锁所需装备名列表（全部拥有才解锁）
# buffs：静态 buff_effect 列表（可为空）；buffs_fn：动态 buff 列表函数
# desc_fn：动态描述函数（可选，缺省用 static_desc）
LEGACY_SKILLS = [
    dict(id=-1, name='风暴降临', type='active', energy_cost=100, cooldown=100,
         duration=50, target='self', requires=[STORM_ARMOR_NAME],
         static_desc='消耗100能量，CD100回合，每次攻击附加(0.07×敏捷+武器等级)真实伤害，持续50回合'),
    dict(id=-2, name='神风烈火', type='passive', duration=-1, target='self',
         requires=[STORM_WEAPON_NAME], buffs_fn=_divine_wind_buffs, desc_fn=_divine_wind_desc),
    dict(id=-3, name='混沌初开', type='passive', duration=-1, target='self',
         requires=[CHAOS_ORB_NAME], buffs_fn=_chaos_buffs, desc_fn=_chaos_desc),
    dict(id=-4, name='光暗侵蚀', type='active', energy_cost=40, cooldown=8,
         duration=4, target='self', requires=[LIGHT_DARK_WEAPON_NAME],
         static_desc='消耗40能量，CD8回合，造成伤害并自身受伤-30%持续4回合'),
    dict(id=-5, name='悲恸光环', type='passive', duration=-1, target='enemy',
         requires=[CROWN_NAME, GREAVES_NAME, RING_NAME], desc_fn=_sorrow_desc),
    dict(id=-6, name='黄昏时刻', type='passive', duration=-1, target='self',
         requires=[SUNSET_ARMOR_NAME],
         static_desc='第10回合自动触发：永久10%最终伤害，并造成一次能量伤害'),
    dict(id=-7, name='黄昏时刻·永恒', type='passive', duration=-1, target='self',
         requires=[SUNSET_WEAPON_NAME], buffs_fn=_sunset_eternal_buffs, desc_fn=_sunset_eternal_desc),
    dict(id=-8, name='噬浪突袭', type='active', energy_cost=20, cooldown=20,
         duration=2, target='self', requires=[SCALE_BOOTS_NAME],
         static_desc='消耗20能量，CD20回合，造成(攻击+能量×2)×(1+0.002暴击)/(1+0.01×有效防御)伤害，并提高5%敏捷2回合',
         buff_effect=[{'name': '噬浪疾步', 'stat': 'agility_percent', 'amount': 5}]),
    dict(id=-9, name='冥域', type='active', energy_cost=80, cooldown=50,
         duration=1, target='enemy', requires=[WU_JIN_MING_YU], desc_fn=_nether_desc),
    dict(id=-10, name='赐剑长驱', type='active', energy_cost=50, cooldown=8,
         duration=5, target='self', requires=[WANG_MING_ZHAN_KAI],
         buffs_fn=_bestow_sword_buffs, desc_fn=_bestow_sword_desc),
    dict(id=-11, name='暗影狂袭', type='passive', duration=-1, target='self',
         requires=[AN_YING_MO_MIAN], buffs_fn=_dark_assault_buffs, desc_fn=_dark_assault_desc),
    dict(id=-12, name='破穿棘刺', type='active', energy_cost=40, cooldown=8,
         duration=0, target='enemy', requires=[DI_TENG_JI_REN],
         static_desc='消耗40能量，CD8回合，造成伤害并追加回合数×2真实伤害，敌方受伤+10%持续5回合'),
    dict(id=-13, name='遮天蔽日', type='passive', duration=-1, target='self',
         requires=[FU_TIAN_MO_CHAN], desc_fn=_sky_cover_desc),
    dict(id=-14, name='轻盈之语', type='active', energy_cost=70, cooldown=10,
         duration=0, target='self', requires=[ZI_RAN_ZHI_JI], desc_fn=_light_words_desc),
    dict(id=-15, name='地脉冲爆', type='active', energy_cost=80, cooldown=10,
         duration=0, target='enemy', requires=[JI_YU_SHEN_JIA], desc_fn=_earth_pulse_desc),
    dict(id=-16, name='绝对防御', type='passive', duration=-1, target='self',
         requires=[JI_YU_SHEN_JIA], static_desc='最终受伤-5%'),
    dict(id=-17, name='天命所归', type='passive', duration=-1, target='self',
         requires=[ZHEN_MING_XUE_SHI], desc_fn=_destiny_desc),
    dict(id=-18, name='长明无忧', type='passive', duration=-1, target='self',
         requires=[YIN_MI_CHANG_MING], desc_fn=_eternal_peace_desc),
    dict(id=-19, name='幽幕暴动', type='active', energy_cost=30, cooldown=18,
         duration=0, target='self', requires=[YOU_MU_BAO_DONG_PAO], desc_fn=_dark_riot_desc),
]


def legacy_entry_by_id(skill_id):
    for entry in LEGACY_SKILLS:
        if entry['id'] == skill_id:
            return entry
    return None


def legacy_entry_by_name(name):
    for entry in LEGACY_SKILLS:
        if entry['name'] == name:
            return entry
    return None


def entry_desc(entry, player):
    if entry.get('desc_fn'):
        return entry['desc_fn'](player)
    return entry.get('static_desc', '')


def entry_buffs(entry, player):
    """返回技能的全部 buff_effect 列表（已按玩家属性动态计算）。"""
    if entry.get('buffs_fn'):
        return entry['buffs_fn'](player)
    return entry.get('buff_effect') or []


def build_skills(entry, player):
    """根据目录条目与玩家属性构建 Skill 对象（可能多个 buff 对应多个被动 Skill）。"""
    buffs = entry_buffs(entry, player)
    desc = entry_desc(entry, player)
    if not buffs:
        buffs = [None]
    return [Skill(id=entry['id'], name=entry['name'], type=entry['type'],
                  power=0, energy_cost=entry.get('energy_cost', 0),
                  buff_effect=buff, duration=entry.get('duration', 0),
                  target=entry.get('target', 'self'), desc=desc,
                  cooldown=entry.get('cooldown', 0)) for buff in buffs]


def unlocked_legacy_skills(equipped_names, player):
    """返回已解锁的已有装备技能条目列表（保持目录顺序）。"""
    result = []
    for entry in LEGACY_SKILLS:
        if all(name in equipped_names for name in entry['requires']):
            result.append(entry)
    return result


def skill_id_to_name(skill_id):
    """ID -> 技能名（覆盖已有装备技能与新装备技能）。"""
    entry = legacy_entry_by_id(skill_id)
    if entry:
        return entry['name']
    for name, d in NEW_EQUIPMENT_SKILLS.items():
        if d['id'] == skill_id:
            return name
    return None


def skill_name_to_id(name):
    entry = legacy_entry_by_name(name)
    if entry:
        return entry['id']
    d = NEW_EQUIPMENT_SKILLS.get(name)
    if d:
        return d['id']
    return None
