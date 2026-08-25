class Equipment:
    def __init__(self, id, name, slot, price=0, attack=0, defense=0, hp=0,
                 energy=0, crit=0, pen=0, agility=0):
        self.id = id
        self.name = name
        self.slot = slot
        self.price = price
        self.base_attack = float(attack)
        self.base_defense = float(defense)
        self.base_hp = float(hp)
        self.base_energy = float(energy)
        self.base_crit = float(crit)
        self.base_pen = float(pen)
        self.base_agility = float(agility)

    def get_stats(self, level=0, quality=100, refine_stat=None, refine_percent=100):
        # 强化系数：每一级强化乘以 1.15（系数保留更多位小数，避免精度损失）
        factor = round((1.15 ** level) * (quality / 100.0), 6)
        # 计算过程保留两位小数
        stats = {
            'attack': round(self.base_attack * factor, 2),
            'defense': round(self.base_defense * factor, 2),
            'hp': round(self.base_hp * factor, 2),
            'energy': round(self.base_energy * factor, 2),
            'crit': round(self.base_crit * factor, 2),
            'pen': round(self.base_pen * factor, 2),
            'agility': round(self.base_agility * factor, 2)
        }
        # 淬炼：只对被选中属性按淬炼百分比放大，其余属性不变（计算保留两位小数）
        if refine_stat and refine_stat in stats:
            stats[refine_stat] = round(stats[refine_stat] * refine_percent / 100.0, 2)
        # 最终结果四舍五入为整数
        return {k: round(v) for k, v in stats.items()}