
class Effect:
    def __init__(self, hit: int, fighter):
        self.hit = hit
        self.fighter = fighter

    def __str__(self):
        return f"Hit {self.hit} on {self.fighter}"