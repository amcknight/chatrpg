from random import randrange
from fight.effect import Effect

from fight.fighter import Fighter

class Brawl:
    def __init__(self, place: str, left: Fighter, right: Fighter):
        self.place = place
        self.left = left
        self.right = right

        self.ran = False
        self.log = []
        self.max_steps = 100

    def run(self):
        while not self.outcome():
            left_state = list(map(lambda f: f.state(), self.left))
            right_state = list(map(lambda f: f.state(), self.right))
            next_fighter, isLeft = self.pick_next_fighter()
            effect = next_fighter.act(self.brawl_view(next_fighter, isLeft))
            self.apply_effect(effect)
            self.log.append((left_state, right_state, next_fighter.__str__(), effect.__str__()))
        self.ran = True

    def outcome(self):
        if len(list(filter(lambda f: f.alive(), self.left))) == 0:
            return "Left Dead"
        if len(list(filter(lambda f: f.alive(), self.right))) == 0:
            return "Right Dead"
        if len(self.log) > self.max_steps:
            return "Tired"

    def get_living(self):
        return list(filter(lambda f: f.alive(), self.left))
            
    def fighters_on_side(self, isLeft, exclude=None):
        fighters = self.left if isLeft else self.right
        if exclude:
            return fighters[:].remove(exclude)
        else:
            return fighters

    def side(self, fighter):
        if fighter in self.left:
            return True
        elif fighter in self.right:
            return False
        else:
            raise Exception("Fighter not on either side")

    def team(self, fighter):
        return self.left if self.side(fighter) else self.right

    def brawl_view(self, fighter, isLeft) -> tuple[list[Fighter], list[Fighter]]:
        return self.fighters_on_side(isLeft, exclude=fighter), self.fighters_on_side(not isLeft)

    def pick_next_fighter(self) -> tuple[Fighter, bool]:
        fighter = None
        # TODO: Infinite loop if everyone dead. Picks by random.
        while not (fighter and fighter.alive()):
            num_fighters = len(self.left) + len(self.right)
            i = randrange(0,num_fighters)
            fighter, isleft = self.get_fighter_side(i)
        return fighter, isleft

    def get_fighter_side(self, i):
        fighters = self.left + self.right
        return fighters[i], i < len(self.left)
    
    def apply_effect(self, effect: Effect):
        effect.fighter.apply_hit(effect.hit)

    def __str__(self):
        left = list(map(str, self.left))
        right = list(map(str, self.right))
        return " ".join(left) + "  vs  " + " ".join(right)
