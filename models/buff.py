class Buff:
    def __init__(self, name, stat, amount, duration, is_debuff=False):
        self.name = name
        self.stat = stat
        self.amount = amount
        self.remaining = duration
        self.is_debuff = is_debuff
        self.created_turn = -1

    def tick(self):
        if self.remaining == -1:
            return False
        self.remaining -= 1
        return self.remaining <= 0