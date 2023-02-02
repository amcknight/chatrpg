import os
import time
import logging
import json
import threading
from battle import Battle, Fighter
from store import Store
from random import choice, randrange
from twitchio.ext import commands
from twitchio.channel import Channel

logging.basicConfig(filename='log.log', level=logging.WARN)


def sec():
    return int(time.time())


class Bot(commands.Bot):
    def __init__(self):
        self.v = '0.1.04'
        self.first_message = 'HeyGuys'
        self.last_time = sec()
        self.chatters = []
        self.mangort_here = False

        self.places = {"home":"home", "garden":"to the garden"}
        self.fight_places = ["garden"]
        self.locked_players = []
        self.locked_places = []

        self.store = Store()
        try:
            self.store.connect()
            self.was_connected = True
        except:
            self.was_connected = False

        name = os.environ['BOT_NICK']
        super().__init__(
            token=os.environ['TMI_TOKEN'],
            client_secret=os.environ['CLIENT_SECRET'],
            nick=name,
            prefix='!',
            initial_channels=[os.environ['CHANNEL']]
        )

    def default_channel(self):
        return self.connected_channels[0]

    def since_last(self):  
        now = sec()
        since = now - self.last_time
        self.last_time = now
        return since

    # TODO: This needs to be called more regularly
    def update(self):
        self.store.update_xp(self.chatters, self.since_last())
        self.process_shown_events()
        self.process_schedule()

    def process_shown_events(self):
        event = self.store.get_shown()
        if not event: return

         # TODO: Not all events are going to be battle logs. Also probably should parse to a dedicated object. None of this works right.
        battle_log = json.loads(event)
        players = ['mangort'] # battle_log.get_team()
        self.apply_battle_log(battle_log)
        for player in players:
            self.locked_players.remove(player)

    def apply_battle_log(self, battle_log):
        # update stats like HP
        # give item drops to players
        # move dead players home and penalize
        print(battle_log)
        pass

    def process_schedule(self):
        place = self.store.next_brawl_place()
        if place:
            players = self.store.get_players_at(place)
            for player in players:
                self.locked_players.append(player)
            battle = self.build_battle(place, players)
            battle_log = battle.fight()
            self.store.add_event(json.dumps(battle_log))

    def build_battle(self, place, players):
        team = list(map(self.store.get_fighter, players))
        rivals = self.generate_rivals(place)

        return Battle(team, rivals)
    
    def generate_rivals(self, place):
        # TODO: Something reasonable
        return [
            Fighter(2, 9, 3, 1, 3, 0),
            Fighter(2, 9, 3, 1, 3, 0),
            Fighter(4, 14, 4, 1, 4, 1)
        ]


    ##### Command Management: #####

    @commands.command()
    async def me(self, ctx):
        if not self.store.connected(): return
        author = ctx.author.name
        name = author.lower()
        job = self.store.get_job(name)
        lvl = self.store.get_level(name)
        xp = self.store.get_xp_left(name)
        await ctx.send(f'{author}: Level {lvl} {job.capitalize()}. Needs {xp} XP')

    @commands.command()
    async def go(self, ctx, *args):
        if not await self.active(): return
        author = ctx.author.name
        name = author.lower()

        if name in self.locked_players:
            await ctx.send(f'{author} is locked until the brawl')
            return

        new_place = args[0].strip().lower()
        
        if new_place not in self.places.keys():
            await ctx.send(f'try: {", ".join(self.places.keys())}')
            return

        place = self.store.get_place(name)
        if new_place == place:
            await ctx.send(f"{author} you're already there")
        else:
            self.store.set_place(name, new_place)
            await ctx.send(f'{author} went {self.places[new_place]}')

    @commands.command()
    async def fight(self, ctx):
        if not await self.active(): return

        author = ctx.author.name
        name = author.lower()
        if name in self.locked_players:
            await ctx.send(f'{author} is locked until the brawl')
            return

        place = self.store.get_place(name)
        if place in self.locked_places:
            await ctx.send(f'{place} is locked until the brawl')
            return
        
        if place not in self.fight_places:
            await ctx.send(f"You can't fight here")
        else:
            wait = 60
            sched_time = sec() + wait
            self.store.schedule_brawl(place, sched_time)
            self.locked_players.append(name)
            self.locked_places.append(place)
            await ctx.send(f'{author} is brawling at {place} in {wait} seconds! Be there to fight or get out!')

    @commands.command()
    async def version(self, ctx):
        await ctx.send(f'v{self.v}')

    def is_command(self, content):
        # chr(1) is a Start of Header character that shows up invisibly in /me ACTIONs
        return content[0] in '!/' or content.startswith(chr(1)+'ACTION ')
    
    ##### Event Management: #####

    async def event_ready(self):
        'Called once when the bot goes online.'
        print(f"{self.nick} is online!")
        await self.default_channel().send(self.first_message)

    async def event_raw_data(self, data):
        logging.info(data)

    async def event_join(self, channel, user):
        name = user.name.lower()
        if name == 'mangort':
            await self.mangort_arrived()

        if name not in self.chatters:
            self.chatters.append(name)

    async def event_part(self, user):
        name = user.name.lower()

        if name == 'mangort':
            await self.mangort_left()

        if name in self.chatters:
            self.chatters.remove(name)

    async def event_message(self, msg):
        'Runs every time a message is sent in chat.'

        if not msg.author:
            return # No author. Maybe because from first_message?

        channel = msg.channel
        content = msg.content
        name = msg.author.name.lower()
        if name == self.nick.lower():
            return

        if name == 'mangort':
            await self.mangort_arrived()

        if await self.active():
            self.update()

        if self.is_command(content):
            await self.handle_commands(msg)

    async def event_error(self, error):
        print(error)
        logging.error(f"Event Error: {error}")
        await self.default_channel().send("/me :boom: :bug: mangort")

    ##### Mangort and Store state management: #####

    async def mangort_arrived(self):
        if self.mangort_here: return
        self.since_last()
        self.mangort_here = True
        await self.default_channel().send("hi mangort")

    async def mangort_left(self):
        if not self.mangort_here: return
        if await self.active():
            self.update()
        self.chatters = []
        self.mangort_here = False
        await self.default_channel().send("bye mangort")

    async def active(self):
        connected = self.store.connected()
        await self.check_connection_change(connected)
        if not connected:
            try:
                self.store.connect()
            except:
                pass
        return connected and self.mangort_here

    async def check_connection_change(self, connected):
        if self.was_connected == connected: return
        if connected:
            await self.default_channel().send("/me :disk: :)")
        else:
            await self.default_channel().send("/me :disk: :(")
        self.was_connected = connected

if __name__ == "__main__":
    bot = Bot()
    bot.run()
