import os
import time
import logging
import threading
from math import floor
from store import Store
from random import choice, randrange
from twitchio.ext import commands
from twitchio.channel import Channel

logging.basicConfig(filename='everything.log', level=logging.INFO)


class Bot(commands.Bot):
    def __init__(self):
        self.v = '0.0.04'
        self.first_message = 'HeyGuys'
        self.active = True
        self.chatters = []
        self.last_time = int(time.time())
        self.store = Store()

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

    def is_command(self, content):
        # chr(1) is a Start of Header character that shows up invisibly in /me ACTIONs
        return content[0] in '!/' or content.startswith(chr(1)+'ACTION ')

    def is_emote_command(self, content):
        return content.startswith('mangor7')

    async def event_ready(self):
        'Called once when the bot goes online.'
        print(f"{self.nick} is online!")
        await self.connected_channels[0].send(self.first_message) # Need to do this when no context available

    async def event_raw_data(self, data):
        logging.info(data)

    async def event_join(self, channel, user):
        name = user.name.lower()
        if name == 'mangort':
            await channel.send('Game on catJAM')
            self.active = True
            self.since_last()

        if name not in self.chatters:
            self.chatters.append(name)

    async def event_part(self, user):
        name = user.name.lower()

        if name == 'mangort':
            await self.default_channel().send('Game off')
            self.since_last()
            self.active = False

        if name in self.chatters:
            self.chatters.remove(name)

    async def event_message(self, msg):
        'Runs every time a message is sent in chat.'

        if not msg.author:
            return # No author. Maybe because from first_message?

        channel = msg.channel
        content = msg.content
        author = msg.author.name
        if author.lower() == self.nick.lower():
            return

        if self.active:
            self.store.update_xp(self.chatters, self.since_last())

        if self.is_command(content):
            await self.handle_commands(msg)
        elif self.is_emote_command(content):
            await self.handle_emote_command(channel, content, author)

    async def handle_emote_command(self, channel, content, author):
        words = content.split(' ')

    @commands.command()
    async def xp(self, ctx):
        author = ctx.author.name
        axp = self.store.get_xp(author.lower())
        await ctx.send(f'{author} has {floor(axp/60)} XP')

    @commands.command()
    async def version(self, ctx):
        await ctx.send(f'peepoHmm v{self.v}')

    @commands.command()
    async def help(self, ctx):
        await ctx.send(f"{self.nick} commands: https://github.com/amcknight/chatrpg/blob/main/Commands.md")

    async def event_error(self, error):
        print(error)
        logging.error(error)
        await self.connected_channels[0].send("/me :boom: PepeHands there are bugs in my brain, mangort")

    def since_last(self):  
        now = int(time.time())
        since = now - self.last_time
        self.last_time = now
        return since

    def minutely(self):
        pass

def periodic(b):
    while True:
        time.sleep(60)
        b.minutely()


if __name__ == "__main__":
    bot = Bot()
    t = threading.Thread(target=periodic, args=(bot,), daemon=True)
    t.start()
    bot.run()
