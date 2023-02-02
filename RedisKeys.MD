Variables:

epoch_seconds = INT
event = JSON
event_id = INT
job = ENUM
place = ENUM
player = STRING

Keys:

brawltimes = ZSET <place>:<epoch_seconds>
events = LIST <event>
place:<place>:players = SET <player>
<player>:xp:<job> = INT
<player>:job = <job>
<player>:place = <place>
shown = LIST <event_id>
