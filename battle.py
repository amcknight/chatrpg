from random import randrange
from fight.fighter import Fighter
from fight.brawl import Brawl

if __name__ == "__main__":
    p1 = Fighter('id1', 'Joe', 'https://cdn.betterttv.net/emote/5ed3bde8f54be95e2a838279/3x.webp', 4, 12, 5, 1, 4, 3)
    p2 = Fighter('id2', 'Moe', 'https://cdn.betterttv.net/emote/5ed3bde8f54be95e2a838279/3x.webp', 6, 11, 5, 1, 4, 1)
    slime1 = Fighter('id51', 'Slime', '', 2, 9, 3, 1, 3, 0)
    slime2 = Fighter('id52', 'Slime', '', 2, 9, 3, 1, 3, 0)
    bull = Fighter('id53', 'Bull', '', 4, 14, 4, 1, 4, 1)

    b = Brawl('boxing ring', [p1, p2], [slime1, slime2, bull])
    b.run()
    print(f'Place: {b.place}')
    print(f'Outcome: {b.outcome()}')
    for step in b.log:
        print(f'Log:{step}')    
