from twitchio.ext import commands

# importing functions in twitterSearch.py
from lolSearch import *
import sqlite3, datetime
import database, factor

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

    # !team command
    # Searches either a cache or Factor.gg to get the players in the game where the current streamer is playing
    # Check cache to see if there is an entry within the past 5 minutes.
    # If not, call search and update the cache.
    @commands.command()
    async def team(self, ctx: commands.Context):
        channel = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        twitch_id = [channel]
        # If user does not exist in the cache, call search and update the cache.
        c.execute("SELECT * FROM cache WHERE twitch_id = ?", (twitch_id))
        curCursor = c.fetchone()
        if curCursor is None:
            c.execute("SELECT * FROM streamers WHERE twitch_id = ?", (twitch_id))
            curCursor = c.fetchone()
            if curCursor[2] == '':
                await ctx.send(f'No Champions Queue name found, please update with !cqname')
            else:
                # Search will return the string to be printed
                # curCursor format is (id, 'twitch name', 'Champions Queue name')
                output = factor.search(curCursor[2])
                if output is None:
                    await ctx.send(f'Match not found, if this is an error, please verify !cqname is set correctly')
                else:
                    # Updates cache
                    currentTime = datetime.datetime.now()
                    c.execute(
                        "REPLACE into cache (team, update_time, twitch_id) VALUES (?, ?, ?) ", (
                            output,
                            currentTime,
                            channel
                        )
                    )
                    conn.commit()
                    await ctx.send(f'{output}')
        # User exists in cache, check if version in cache is less than 5 minutes old.
        # If version in cache was created in last 5 minutes, use that
        # Otherwise, perform search
        else:
            c.execute("SELECT * FROM streamers WHERE twitch_id = ?", (twitch_id))
            curCursor = c.fetchone()
            if curCursor[2] == '':
                await ctx.send(f'No Champions Queue name found, please update with !cqname')
            else:
                c.execute("SELECT * FROM cache WHERE twitch_id = ?", (twitch_id))
                curCursor = c.fetchone()
                # curCursor[2] is the update_time
                currentTime = datetime.datetime.now()
                cacheTime = datetime.datetime.strptime(curCursor[2], '%Y-%m-%d %H:%M:%S.%f')
                duration = currentTime - cacheTime
                duration_in_s = duration.total_seconds()
                if duration_in_s < 300:
                    await ctx.send(f'{curCursor[1]}')
                else:
                    c.execute("SELECT * FROM streamers WHERE twitch_id = ?", (twitch_id))
                    curCursor = c.fetchone()
                    # Search will return the string to be printed
                    # curCursor format is (id, 'twitch name', 'Champions Queue name')
                    output = factor.search(curCursor[2])
                    if output is None:
                        await ctx.send(f'Match not found, if this is an error, please verify !cqname is set correctly')
                    else:
                        # Updates cache
                        currentTime = datetime.datetime.now()
                        c.execute(
                            "REPLACE into cache (team, update_time, twitch_id) VALUES (?, ?, ?) ", (
                                output,
                                currentTime,
                                channel
                            )
                        )
                        conn.commit()
                        await ctx.send(f'{output}')
        # Link is sent in chat
    
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
    
    # !cqname command
    # Associates the streamers database with a user's Twitch name with their Chmapions Queue name
    @commands.command()
    async def cqname(self, ctx: commands.Context, *args):
        # Channel command as a string
        curChannel = (str(ctx.channel)).replace("<Channel name: ", "").strip('\>')
        if (len(args) == 0):
            await ctx.send(f"Format is !cqname [Name]")
        elif (len(args) == 1):
            cqName = str(args[0]).lower()
            # Updates database
            c.execute(
                "UPDATE streamers SET factor_id = ? WHERE twitch_id = ?", (
                    cqName, 
                    curChannel
                )
            )
            conn.commit()
            await ctx.send(f"Champions Queue name for {curChannel} set as {cqName}!")
        else:
            if (curChannel == "deadfracture"):
                channelName = str(args[0]).lower()
                cqName = ' '.join(args[1:])
                # Updates database
                c.execute(
                    "UPDATE streamers SET factor_id = ? WHERE twitch_id = ?", (
                        cqName, 
                        channelName
                    )
                )
                conn.commit()
                await ctx.send(f"Champions Queue name for {channelName} set as {cqName}!")
            
    
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
