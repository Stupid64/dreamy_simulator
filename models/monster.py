class Monster:
    def __init__(self, id, name, type, attack, defense, hp, agility, skill_pool=None,
                 gold=0, exp=0, defend_chance=0.4, dungeon_id=0, dungeon_name="",
                 world_boss=False):
        self.id = id
        self.name = name
        self.type = type
        self.attack = float(attack)
        self.defense = float(defense)
        self.max_hp = float(hp)
        self.hp = float(hp)
        self.agility = float(agility)
        self.gold = gold
        self.exp = exp
        self.crit = 0
        self.defend_chance = defend_chance
        self.skill_pool = skill_pool if skill_pool else []
        self.buffs = []
        self.dungeon_id = dungeon_id
        self.dungeon_name = dungeon_name
        self.world_boss = world_boss