import asyncio
import os
import time
import logging
import json
from words import anded, ored
from fight.brawl import Brawl
from fight.fighter import Fighter
from store import Store
from twitchio.ext import commands

logging.basicConfig(filename='log.log', level=logging.INFO)


def sec():
    return int(time.time())


class Bot(commands.Bot):
    def __init__(self):
        self.v = '0.1.10'
        self.first_message = 'HeyGuys'
        self.last_time = sec()
        self.chatters = []
        self.mangort_here = False

        self.places = {"home":"home", "garden":"to the garden"}
        self.fight_places = ["garden"]
        self.locked_players = set()
        self.locked_places = set()

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
    async def update(self, channel):
        self.store.update_xp(self.chatters, self.since_last())
        await self.process_shown_event(channel)

    async def process_shown_event(self, channel):
        event = self.store.next_shown()
        if not event: return

         # TODO: Not all events are going to be brawl logs
        brawl_info = json.loads(event)
        players = brawl_info['left_names']
        place = brawl_info['place']
        self.apply_brawl_log(brawl_info)
        self.locked_players -= set(players)
        self.locked_places.remove(place)
        players_str = anded(players)
        outcome_str = brawl_info['outcome']
        if outcome_str == 'Right Dead':
            await channel.send(f'{players_str} fought and won! :)')
        elif outcome_str == 'Left Dead':
            await channel.send(f'{players_str} fought and lost! :(')
        elif outcome_str == 'Tired':
            await channel.send(f'{players_str} got tired of fighting. Tie, I guess. :/')
        else:
            await channel.send(f'{players_str}... unknown battle outcome? mangort')


    def apply_brawl_log(self, brawl_info):
        # TODO:
        # update stats like HP
        # give item drops to players
        # move dead players home and penalize
        pass

    async def process_schedule(self, channel):
        place = self.store.next_brawl_place()
        if not place: return 

        players = self.store.get_players_at(place)
        if len(players) < 1:
            raise Exception('No players in brawl!')

        for player in players:
            #TODO: Check that pic is downloaded here
            self.locked_players.add(player)
        
        brawl = self.build_brawl(place, players)
        await channel.send(f"{anded(list(map(lambda f: f.name, brawl.left)))} are queued to brawl {anded(list(map(lambda f: f.name, brawl.right)))} in {brawl.place}!")
        brawl.run()
        self.store.add_event(brawl.to_json())

    async def reset(self, ctx):
        self.store.send_all_home()

        places = self.store.clear_brawls()
        if len(places) > 0:
            await ctx.send(f'Brawls canceled in {" and ".join(places)}')
        
        events = self.store.clear_events()
        if len(events) > 0:
            await ctx.send(f'{len(events)} brawls stifled')
        
        if len(self.locked_players) > 0:
            await ctx.send(f'Unlocked players: {anded(self.locked_players)}')
            self.locked_players = set()

        if len(self.locked_places) > 0:
            await ctx.send(f'Unlocked places: {anded(self.locked_places)}')
            self.locked_places = set()
        
        shown_events = self.store.clear_shown()
        if len(shown_events) > 0:
            await ctx.send(f'{len(shown_events)} brawls revoked')


    def build_brawl(self, place, players):
        team = list(map(self.store.get_fighter, players))
        rivals = self.generate_rivals(place)

        return Brawl(place, team, rivals)
    
    def generate_rivals(self, place):
        # TODO: Something reasonable
        return [
            Fighter('BigCat1', 'Bigcat', 2, 9, 3, 1, 3, 0),
            Fighter('BigCat2', 'Bigcat', 2, 9, 3, 1, 3, 0),
            Fighter('BigCat3', 'Bigcat', 4, 14, 4, 1, 4, 1)
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
    async def home(self, ctx):
        author = ctx.author.name
        name = author.lower()
        if name == 'mangort':
            await self.reset(ctx)

    @commands.command()
    async def butt(self, ctx):
        author = ctx.author.name
        name = author.lower()
        if name == 'buttsbot':
            await ctx.send('buttsbot pls')

    @commands.command()
    async def go(self, ctx, *args):
        if not await self.active(): return
        author = ctx.author.name
        name = author.lower()

        if name in self.locked_players:
            place = self.store.get_place(name)
            await ctx.send(f'{author} is locked until the {place} brawl')
            return

        if not args or len(args) < 1:
            await ctx.send(f'try: {ored(self.places.keys())}')
            return

        new_place = args[0].strip().lower()
        if new_place not in self.places.keys():
            await ctx.send(f'try: {ored(self.places.keys())}')
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
            place = self.store.get_place(name)
            await ctx.send(f'{author} is waiting for the {place} brawl')
            return

        place = self.store.get_place(name)
        if place in self.locked_places:
            await ctx.send(f"There's already a brawl about to happen in {place}")
            return
        
        if place not in self.fight_places:
            await ctx.send(f"You can't fight here")
        else:
            wait = 10
            self.locked_players.add(name)
            self.locked_places.add(place)
            await ctx.send(f'{author} is brawling at {place} in {wait} seconds! Be there to fight or get out!')
            await asyncio.sleep(wait)
            await self.queue_brawl(ctx, place)

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
        channel = user.channel

        if name == 'mangort':
            await self.mangort_left(channel)

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
            await self.update(channel)

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

    async def mangort_left(self, channel):
        if not self.mangort_here: return
        if await self.active():
            await self.update(channel)
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
