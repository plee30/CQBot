from twitchio.ext import commands

# importing functions in twitterSearch.py
from twitterSearch import *
import database

access_token = os.environ.get("TWITCH_ACCESS_TOKEN")

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=access_token, prefix='!', initial_channels=database.list())

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

    # !team command
    # Searches @ChampionsQueue on Twitter for their most recent tweet where the specified streamer was mentioned
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
    
    # !join command
    # Users can use !join on DeadFracture's channel to send DeadFractureBot to their channel
    # DeadFracture can also use this command to send the bot to anyone's channel
    @commands.command()
    async def join(self, ctx: commands.Context, *args):
        # Username of the person who used the command (sender) as a string
        sender = str(ctx.author.name)
        # Channel command was used as a string
        curChannel = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        
        # Can only !join on DeadFracture's channel
        if (curChannel != "deadfracture"):
            await ctx.send("Command only available on ttv/DeadFracture")
            pass
        else:
            # If no argument, joins the senders channel
            if (len(args) == 0):
                toJoin = [sender]
                database.add(sender)
                await bot.join_channels(toJoin)
                await ctx.send(f"Joined {sender}'s channel!")
            else:
                # If sender is DeadFracture, bot will be sent
                if (sender == "deadfracture"): 
                    channelName = str(args[0]).lower()
                    toJoin = [channelName]
                    database.add(channelName)
                    await bot.join_channels(toJoin)
                    await ctx.send(f"Joined {channelName}!")
                # If sender is not DeadFracture, bot will not be sent
                else:
                    await ctx.send(f"I currently do not support being sent to someone else's channel :(")
    
    # !leave command
    # DeadFracture bot will leave the channel when asked               
    @commands.command()
    async def leave(self, ctx: commands.Context, *args):
        sender = str(ctx.author.name)
        curChannel = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        if (len(args) == 0):
            if (curChannel == sender):
                if sender == "deadfracture":
                    return
                toLeave = [sender]
                database.remove(sender)
                await bot.part_channels(toLeave)
                await ctx.send(f"Left {sender}'s channel!")
        else:
            if (sender == "deadfracture"): 
                channelName = str(args[0]).lower()
                if channelName == "deadfracture":
                    return               
                toLeave = [channelName]
                database.remove(channelName)
                await bot.part_channels(toLeave)
                await ctx.send(f"Left {channelName}!")
            else:
                await ctx.send(f"I currently do not support being sent to someone else's channel :(")

    @commands.command()
    async def help(self, ctx: commands.Context):
        # Gets the channel the command was called in as a string
        await ctx.send(f"!team (optional: username), !join, !leave")

    # @commands.command()
    # async def test(self, ctx: commands.Context, *args):
    #     # Gets the channel the command was called in as a string
    #     await ctx.send(f"User is {ctx.author.name}")
    #     await ctx.send(f"Args are {args}")
    
    @commands.command()
    async def where(self, ctx: commands.Context):
        # Gets the channel the command was called in as a string
        await ctx.send(f"{database.list()}")


bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
