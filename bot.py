import os
import time
import logging
from random import choice, randrange
from twitchio.ext import commands
from twitchio.channel import Channel

logging.basicConfig(filename='everything.log', level=logging.INFO)


class Bot(commands.Bot):
    def __init__(self):
        self.v = '0.0.01'
        self.first_message = 'HeyGuys'
        self.active = True

        name = os.environ['BOT_NICK']
        super().__init__(
            token=os.environ['TMI_TOKEN'],
            client_secret=os.environ['CLIENT_SECRET'],
            nick=name,
            prefix='!',
            initial_channels=[os.environ['CHANNEL']]
        )

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

    async def event_message(self, msg):
        'Runs every time a message is sent in chat.'

        if not msg.author:
            return # No author. Maybe because from first_message?

        channel = msg.channel
        content = msg.content
        author = msg.author.name
        if author.lower() == self.nick.lower():
            return

        if self.is_command(content):
            await self.handle_commands(msg)
            return

        if self.is_emote_command(content):
            await self.handle_emote_command(channel, content, author)

    async def handle_emote_command(self, channel, content, author):
        words = content.split(' ')
        if (words[0] == 'mangor7Ban'):
            banned = " ".join(words[1:]).strip()
            if len(banned) == 0:
                time.sleep(0.5)
                await channel.send(f'/me {author} LUL')

    async def event_raw_usernotice(self, channel: Channel, tags: dict):
        if tags['msg-id'] == 'raid':
            await channel.send(f'!so {tags["display-name"]}')
        elif tags['msg-id'] in ['sub', 'resub', 'subgift', 'submysterygift']:
            logging.info("SUB:::")
            logging.info(tags)
            pass # Need to collect groups of gifts into a single message if using this
        elif tags['msg-id'] == 'host':
            logging.info("HOST:::")
            logging.info(tags)
        elif tags['nsg-id'] == 'announcement':
            logging.info("ANNOUNCE:::")
            logging.info(tags)
        else:
            logging.info("RAW USER NOTICE:::")
            logging.info(tags)
        return await super().event_raw_usernotice(channel, tags)

    @commands.command()
    async def version(self, ctx):
        await ctx.send(f'peepoHmm v{self.v}')

    @commands.command()
    async def help(self, ctx):
        await ctx.send("goRtPG commands: https://github.com/amcknight/chatrpg/blob/main/Commands.md")

    async def event_error(self, error):
        print(error)
        logging.error(error)
        await self.connected_channels[0].send("/me :boom: PepeHands there are bugs in my brain, mangort")


if __name__ == "__main__":
    Bot().run()
