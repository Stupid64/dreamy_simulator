class Player:
    BASE_ATTACK = 20.0
    BASE_DEFENSE = 10.0
    BASE_HP = 100.0
    BASE_ENERGY = 30.0
    BASE_CRIT = 5.0
    BASE_PEN = 0.0
    BASE_AGILITY = 5.0

    def __init__(self, name="勇者", level=1):
        self.name = name
        self.level = level
        self._calc_raw_stats()
        self.gear = {
            '武器': None,
            '护甲': None,
            '头盔': None,
            '鞋子': None,
            '饰品': None
        }
        self.equipped_skills = []
        self.passive_skills = []
        self._calc_base_stats()

    def set_level(self, level):
        self.level = max(1, level)
        self._calc_raw_stats()
        self._calc_base_stats()

    def _calc_raw_stats(self):
        lv = self.level
        self.raw_hp = self.BASE_HP + (lv - 1) * 5.0
        self.raw_attack = self.BASE_ATTACK + (lv - 1) * 1.0
        self.raw_defense = self.BASE_DEFENSE + (lv - 1) // 2 * 1.0
        self.raw_energy = self.BASE_ENERGY + (lv - 1) // 10 * 1.0
        self.raw_crit = self.BASE_CRIT
        self.raw_pen = self.BASE_PEN
        self.raw_agility = self.BASE_AGILITY

    def equip_item(self, slot, equipment, level=0, quality=100, refine_stat=None, refine_percent=100):
        if slot not in self.gear:
            return
        self.gear[slot] = {
            'equipment': equipment,
            'level': max(0, int(level)),
            'quality': max(100, min(120, int(quality))),
            'refine_stat': refine_stat,
            'refine_percent': refine_percent
        }
        self._calc_base_stats()

    def unequip_item(self, slot):
        if slot in self.gear:
            self.gear[slot] = None
        self._calc_base_stats()

    def apply_passive_skills(self):
        self._calc_base_stats()

    def _calc_base_stats(self):
        self.base_hp = self.raw_hp
        self.base_attack = self.raw_attack
        self.base_defense = self.raw_defense
        self.base_energy = self.raw_energy
        self.base_agility = self.raw_agility
        self.base_crit = self.raw_crit
        self.base_pen = self.raw_pen

        # 装备加成
        for gear_data in self.gear.values():
            if gear_data and gear_data['equipment']:
                eq = gear_data['equipment']
                stats = eq.get_stats(gear_data['level'], gear_data['quality'],
                                     gear_data.get('refine_stat'),
                                     gear_data.get('refine_percent', 100))
                self.base_attack += stats['attack']
                self.base_defense += stats['defense']
                self.base_hp += stats['hp']
                self.base_energy += stats['energy']
                self.base_crit += stats['crit']
                self.base_pen += stats['pen']
                self.base_agility += stats['agility']

        # 百分比被动收集
        percent_effects = {
            'defense_percent': 0.0,
            'attack_percent': 0.0,
            'agility_percent': 0.0,
            'crit_percent': 0.0,
            'hp_percent': 0.0,
            'energy_percent': 0.0,
            'pen_percent': 0.0          # 新增穿透百分比
        }
        for skill in self.passive_skills:
            if skill.type == 'passive' and skill.buff_effect:
                stat = skill.buff_effect.get('stat')
                amount = float(skill.buff_effect.get('amount', 0))
                if stat in percent_effects:
                    percent_effects[stat] += amount
                else:
                    if stat == 'hp':
                        self.base_hp += amount
                    elif stat == 'attack':
                        self.base_attack += amount
                    elif stat == 'defense':
                        self.base_defense += amount
                    elif stat == 'energy':
                        self.base_energy += amount
                    elif stat == 'agility':
                        self.base_agility += amount
                    elif stat == 'crit':
                        self.base_crit += amount
                    elif stat == 'armor_pen' or stat == 'pen':
                        self.base_pen += amount

        # 应用百分比
        if percent_effects['attack_percent'] != 0:
            self.base_attack = round(self.base_attack * (1 + percent_effects['attack_percent'] / 100.0))
        if percent_effects['defense_percent'] != 0:
            self.base_defense = round(self.base_defense * (1 + percent_effects['defense_percent'] / 100.0))
        if percent_effects['agility_percent'] != 0:
            self.base_agility = round(self.base_agility * (1 + percent_effects['agility_percent'] / 100.0))
        if percent_effects['crit_percent'] != 0:
            self.base_crit = round(self.base_crit * (1 + percent_effects['crit_percent'] / 100.0))
        if percent_effects['hp_percent'] != 0:
            self.base_hp = round(self.base_hp * (1 + percent_effects['hp_percent'] / 100.0))
        if percent_effects['energy_percent'] != 0:
            self.base_energy = round(self.base_energy * (1 + percent_effects['energy_percent'] / 100.0))
        if percent_effects['pen_percent'] != 0:                     # 新增
            self.base_pen = round(self.base_pen * (1 + percent_effects['pen_percent'] / 100.0))

        # 保证最低值
        self.base_hp = max(1, round(self.base_hp))
        self.base_attack = max(1, round(self.base_attack))
        self.base_defense = max(0, round(self.base_defense))
        self.base_energy = max(0, round(self.base_energy))
        self.base_crit = max(0, round(self.base_crit))
        self.base_pen = max(0, round(self.base_pen))
        self.base_agility = max(0, round(self.base_agility))

        self.reset_battle_stats()

    def reset_battle_stats(self):
        self.hp = float(self.base_hp)
        self.max_hp = float(self.base_hp)
        self.attack = float(self.base_attack)
        self.defense = float(self.base_defense)
        self.energy = float(self.base_energy)
        self.max_energy = float(self.base_energy)
        self.agility = float(self.base_agility)
        self.crit = float(self.base_crit)
        self.pen = float(self.base_pen)          # 修正为 pen
        self.buffs = []

    def get_weapon_level(self):
        weapon_data = self.gear.get('武器')
        if weapon_data and weapon_data['equipment']:
            return weapon_data['level']
        return 0