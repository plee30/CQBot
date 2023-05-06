from twitchio.ext import commands
import pandas as pd
# importing functions in twitterSearch.py
from lolSearch import *
import sqlite3, datetime
import database, factor, lolSearch

# Connect to the database
conn = sqlite3.connect('cache.db')
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS streamers (
        id INTEGER PRIMARY KEY,
        twitch_id TEXT NOT NULL,
        factor_id TEXT,
        UNIQUE(twitch_id)
    )""")

c.execute(
    """CREATE TABLE IF NOT EXISTS cache (
        id INTEGER PRIMARY KEY,
        team TEXT,
        update_time timestamp,
        twitch_id TEXT UNIQUE NOT NULL,
        FOREIGN KEY (twitch_id)
            REFERENCES streamers (twitch_id)
    )""")


access_token = os.environ.get("TWITCH_ACCESS_TOKEN")
regions = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "TR1", "RU"]

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
                    # Adds streamer to streamers database
                    c.execute(
                        "INSERT OR IGNORE INTO streamers (twitch_id) VALUES (?)", (toJoin)
                    )
                    conn.commit()
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
                
                c.execute(
                    "DELETE FROM streamers WHERE twitchid = ?", (curChannel)
                )
                conn.commit()
                await bot.part_channels(toLeave)
                await ctx.send(f"Left {sender}'s channel!")
        else:
            if (sender == "deadfracture"): 
                channelName = str(args[0]).lower()
                if channelName == "deadfracture":
                    return               
                toLeave = [channelName]
                database.remove(channelName)
                c.execute(
                    "DELETE FROM streamers WHERE twitchid = ?", (channelName)
                )
                conn.commit()
                await bot.part_channels(toLeave)
                await ctx.send(f"Left {channelName}!")
            else:
                await ctx.send(f"I currently do not support leaving someone else's channel in this way :(")
                
    @commands.command()
    async def challenger(self, ctx: commands.Context, *args):
        if (len(args) == 0) or (str(args[0].upper()) not in regions):
            print(str(args[0].upper()))
            print(regions)
            await ctx.send(f"Please specify a region (BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, TR1, RU)")
        else:
            reg = str(args[0]).upper()
            await ctx.send(lowest(reg))
            
    @commands.command()
    async def rank(self, ctx: commands.Context, *args):
        curChannel = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        if curChannel == "shrimp9710":
            to_send = lolSearch.rank("kr", "Toon Zorc")
            await ctx.send(to_send)
        elif curChannel == "deadfracture":
            to_send = lolSearch.rank("kr", "Toon Zorc")
            await ctx.send(to_send)
        elif(len(args) == 0) or (str(args[0].upper()) not in regions):
            print(str(args[0].upper()))
            print(regions)
            await ctx.send(f"Please specify a region (BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, TR1, RU)")
        else:
            reg = str(args[0]).upper()
            await ctx.send(lowest(reg))
    
    @commands.command()
    async def runes(self, ctx: commands.Context, *args):
        curChannel = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        if curChannel == "shrimp9710":
            to_send = lolSearch.runes("kr", "Toon Zorc")
            await ctx.send(f"{to_send[0]} / {to_send[1]} / {to_send[2]} / {to_send[3]} || {to_send[4]} / {to_send[5]} || {to_send[6]} / {to_send[7]} / {to_send[8]}")
        elif curChannel == "deadfracture":
            to_send = lolSearch.runes("kr", "Toon Zorc")
            await ctx.send(f"{to_send[0]} / {to_send[1]} / {to_send[2]} / {to_send[3]} || {to_send[4]} / {to_send[5]} || {to_send[6]} / {to_send[7]} / {to_send[8]}")
        elif(len(args) == 0) or (str(args[0].upper()) not in regions):
            print(str(args[0].upper()))
            print(regions)
            await ctx.send(f"Please specify a region (BR1, EUN1, EUW1, JP1, KR, LA1, LA2, NA1, OC1, TR1, RU)")
        else:
            reg = str(args[0]).upper()
            await ctx.send(lowest(reg))

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
