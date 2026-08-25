class Skill:
    def __init__(self, id, name, type, power=0, energy_cost=0,
                 buff_effect=None, duration=0, target='enemy', desc='', cooldown=0):
        self.id = id
        self.name = name
        self.type = type
        self.power = power
        self.energy_cost = energy_cost
        self.buff_effect = buff_effect
        self.duration = duration
        self.target = target
        self.desc = desc
        self.cooldown = cooldown