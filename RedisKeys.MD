Variables:

event = JSON
job = ENUM
place = ENUM
player = STRING


Keys:

events = LIST <event>
shown = LIST <event>

place:<place>:players = SET <player>

player:<player>:xp:<job> = INT
player:<player>:job = <job>
player:<player>:place = <place>
