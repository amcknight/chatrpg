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

logging.basicConfig(filename='log.log', level=logging.WARN, format='%(levelname)-7s:%(asctime)s> %(message)s', datefmt='%b-%d %H:%M:%S')


def sec():
    return int(time.time())


class Bot(commands.Bot):
    def __init__(self):
        self.v = '0.2.02'
        self.first_message = 'HeyGuys'
        self.last_time = sec()
        self.chatters = set()
        self.streamer_here = False
        self.streamer = 'mangort'

        self.places = {"home":"home", "garden":"to the garden"}
        self.fight_places = ["garden"]
        self.locked_players = set()
        self.locked_places = set()
        self.proxy_profile_gif = 'https://cdn.betterttv.net/emote/60d7a0028ed8b373e421a0e7/3x.webp'

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

    async def poll_shown(self, channel):
        event = self.store.next_shown()
        if event:
            await self.process_shown(channel, event)
        await asyncio.sleep(1)
        await self.poll_shown(channel)

    async def process_shown(self, channel, event):
         # TODO: Not all events are going to be brawl logs
        brawl_info = json.loads(event)
        players = list(map(lambda p: p['name'], brawl_info['left']))
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
            await channel.send(f'{players_str}... unknown battle outcome? {self.streamer}')


    def apply_brawl_log(self, brawl_info):
        # TODO:
        # update stats like HP
        # give item drops to players
        # move dead players home and penalize
        pass

    async def queue_brawl(self, ctx, place):
        players = self.store.get_players_at(place)
        if len(players) < 1:
            raise Exception('No players in brawl! Locking failed?')
        
        for player in players:
            self.locked_players.add(player)
        
        brawl = await self.build_brawl(place, players)
        brawl.run()
        self.store.add_event(brawl.to_json())
        await ctx.send(f"{anded(list(map(lambda f: f.name, brawl.left)))} are brawling {anded(list(map(lambda f: f.name, brawl.right)))} in {brawl.place}!")

    async def reset(self, ctx):
        self.store.send_all_home()
        
        events = self.store.clear_events()
        if len(events) > 0:
            await ctx.send(f'{len(events)} brawls stifled')
        
        if len(self.locked_players) + len(self.locked_places) > 0:
            await ctx.send(f'Unlocked {anded(list(self.locked_players) + list(self.locked_places))}')
            self.locked_players = set()
            self.locked_places = set()
        
        shown_events = self.store.clear_shown()
        if len(shown_events) > 0:
            await ctx.send(f'{len(shown_events)} brawls revoked')

    async def build_brawl(self, place, players):
        team = await self.generate_team(players)
        rivals = self.generate_rivals(place)

        return Brawl(place, team, rivals)
    
    async def generate_team(self, players):
        users = await self.fetch_users(players)
        if not users: raise(f'Somehow no users fetched when fetching {anded(players)}')
        if not len(users) == len(players): raise(f'Somehow less users than players')
        gifs = list(map(lambda user: user.profile_image, users))
        if not gifs: raise(f'Somehow no gifs fetched when fetching {anded(players)}')
        if not len(gifs) == len(users): raise(f'Somehow less gifs than users')

        # TODO: Something correct
        return [Fighter(f'{player}1', player, gif, 4, 12, 5, 1, 4, 3) for (player, gif) in zip(players, gifs)]

    def generate_rivals(self, place):
        # TODO: Something reasonable
        return [
            Fighter('BigCat1', 'Bigcat', 'https://cdn.betterttv.net/emote/5cc23e0012944662cfabc268/3x.webp', 2, 9, 3, 1, 3, 0),
            Fighter('Goose1', 'Goose', 'https://cdn.betterttv.net/emote/5d898f6bd2458468c1f485a1/3x.webp', 4, 14, 4, 1, 4, 1),
            Fighter('BigCat2', 'Bigcat', 'https://cdn.betterttv.net/emote/5cc23e0012944662cfabc268/3x.webp', 2, 9, 3, 1, 3, 0)
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
        if name == self.streamer:
            await self.reset(ctx)
        else:
            await ctx.send(f'Only {self.streamer} can send everyone home')

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
            wait = 30
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
        channel = self.default_channel()
        await channel.send(self.first_message)
        await self.poll_shown(channel)

    async def event_raw_data(self, data):
        logging.info(data)

    async def event_join(self, channel, user):
        name = user.name.lower()
        if name == self.streamer:
            await self.streamer_arrived(channel)

        if name not in self.chatters:
            self.chatters.add(name)

    async def event_part(self, user):
        name = user.name.lower()
        channel = user.channel

        if name == self.streamer:
            await self.streamer_left(channel)

        if name in self.chatters:
            self.chatters.remove(name)

    async def event_message(self, msg):
        if not msg.author: return # No author. Maybe because from first_message?

        name = msg.author.name.lower()
        self.chatters.add(name)
        if name == self.nick.lower(): return

        channel = msg.channel
        if name == self.streamer:
            await self.streamer_arrived(channel)

        if await self.active():
            self.store.update_xp(list(self.chatters), self.since_last())

        content = msg.content
        if self.is_command(content):
            await self.handle_commands(msg)

    async def event_error(self, error):
        print(f"ERROR: {error}")
        logging.error(f"Event Error: {error}")
        await self.default_channel().send(f"/me :boom: :bug: {self.streamer}")

    ##### Streamer and Store state management: #####

    async def streamer_arrived(self, channel):
        if self.streamer_here: return
        self.since_last()
        self.streamer_here = True
        await channel.send(f"hi {self.streamer}")

    async def streamer_left(self, channel):
        if not self.streamer_here: return
        if await self.active():
            self.store.update_xp(list(self.chatters), self.since_last())
        self.chatters = set()
        self.streamer_here = False
        await channel.send(f"bye {self.streamer}")

    async def active(self):
        connected = self.store.connected()
        await self.check_connection_change(connected)
        if not connected:
            try:
                self.store.connect()
            except:
                pass
        return connected and self.streamer_here

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
