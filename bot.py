from twitchio.ext import commands

# importing functions in twitterSearch.py
from twitterSearch import *

access_token = os.environ.get("TWITCH_ACCESS_TOKEN")

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=access_token, prefix='!', initial_channels=['DeadFracture', 'DeadFractureBot'])

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    # Sends link of current team of Champions Queue player
    async def team(self, ctx: commands.Context, *args):
        # If no argument is given, will search for the streamer the command was called in
        if (len(args) == 0):
            toSearch = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        # Otherwise will search for the player specified
        else:
            toSearch = str(args[0])
        # Link is gotten with the search command in twitterSearch.py
        link = search(toSearch)
        # Remove quotation marks at the beginning and end of the string
        link = link.strip('\"')
        # Link is sent in chat
        await ctx.send(f'{link}')
        
    # @commands.command()
    # async def test(self, ctx: commands.Context, *args):
    #     # Gets the channel the command was called in as a string
    #     await ctx.send(args)


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.