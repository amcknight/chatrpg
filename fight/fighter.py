
from fight.effect import Effect
from random import choice

class Fighter:
    def __init__(self, level, vitality, strength, damage, defense, chin):
        self.level = level
        self.vitality = vitality
        self.strength = strength
        self.damage = damage
        self.defense = defense
        self.chin = chin
        self.restore()

    def __str__(self):
        return f"{self.life}/{self.max_life()}"

    def act(self, brawl_view):
        team, rivals = brawl_view
        return Effect(self.max_hit() * 1 * 1, choice(rivals))

    def max_hit(self):
        return self.strength * self.level + self.damage

    def alive(self):
        return self.life > 0

    def restore(self):
        self.life = self.max_life()

    def max_life(self):
        return self.level * self.vitality

    def apply_hit(self, hit):
        harm = int(max(0, (hit - 1 * self.level) / (self.defense * 1) - self.chin))
        self.life -= harm
        if self.life <= 0:
            self.life = 0

    def state(self):
        return self.__str__()
