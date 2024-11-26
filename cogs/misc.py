import discord
from discord.ext import commands
import datetime
from datetime import timedelta, timezone
import asyncio
import json

from ext.database import db

serverDB = db["serverConfig"]

welcomedict = {}


with open("ext/games.json", "r") as f:
    GAMES = json.load(f)


async def get_game(ctx: discord.AutocompleteContext):
    if ctx.value == "":
        return GAMES
    return [game for game in GAMES if ctx.value.lower() in game.lower()]

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.copy_message = False

    @commands.Cog.listener()
    async def on_ready(self):
        d = serverDB.find({})
        for i in d:
            welcomedict[i["_id"]] = i
            del welcomedict[i["_id"]]["_id"]

    @commands.slash_command()
    async def spotify(self, interaction: discord.ApplicationContext, user: discord.Member = None):
        user = user or interaction.user
        user = interaction.guild.get_member(user.id)
        if not user.activities:
            await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)
            return
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                embed = discord.Embed(title=activity.title, description=f"by {activity.artist}", color=activity.color, url=activity.track_url)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Album", value=activity.album, inline=False)
                duration = str(datetime.datetime.utcnow() - activity.start.replace(tzinfo=None)).split(".")[0].split(":", 1)[1]
                tduration = str(activity.duration).split(".")[0].split(":", 1)[1]
                embed.add_field(name="Duration", value=f"{duration} / {tduration}", inline=False)
                embed.set_author(name=user, icon_url=user.display_avatar.url)
                embed.set_footer(text="Started")
                embed.timestamp = activity.created_at
                await interaction.response.send_message(embed=embed)
                return
        await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)

    @commands.user_command(name="Spotify")
    async def _spotify(self, interaction: discord.ApplicationContext, user: discord.Member = None):
        user = user or interaction.user
        user = interaction.guild.get_member(user.id)
        if not user.activities:
            await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)
            return
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                embed = discord.Embed(title=activity.title, description=f"by {activity.artist}", color=activity.color, url=activity.track_url)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Album", value=activity.album, inline=False)
                duration = str(datetime.datetime.utcnow() - activity.start.replace(tzinfo=None)).split(".")[0].split(":", 1)[1]
                tduration = str(activity.duration).split(".")[0].split(":", 1)[1]
                embed.add_field(name="Duration", value=f"{duration} / {tduration}", inline=False)
                embed.set_author(name=user, icon_url=user.display_avatar.url)
                embed.set_footer(text="Started")
                embed.timestamp = activity.created_at
                await interaction.response.send_message(embed=embed)
                return
        await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)

    @commands.command()
    async def snowflake(self, ctx, snowflake, snowflake2=None):
        s = discord.Object(id=snowflake)
        d: datetime.datetime = s.created_at.timestamp()
        if snowflake2:
            s2 = discord.Object(id=snowflake2)
            st: datetime.datetime = s2.created_at.timestamp()
        elif ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            st = msg.created_at.timestamp()
        else:
            st = datetime.datetime.now().timestamp()
        time = str(timedelta(seconds=st - d))
        value = ""
        if "," in time:
            time = time.split(",")
            value += time[0] + " , "
            time = time[1]
        time = time.split(":")
        if int(time[0]) != 0:
            value += time[0] + " hours, "
        if int(time[1]) != 0:
            value += time[1] + " minutes and "
        value += f"{float(time[2]) : .2f}" + " seconds"
        await ctx.reply(value, mention_author=False)

    @commands.slash_command(name="say", description="say something as the bot", guild_ids=[906909577394663484])
    @commands.is_owner()
    async def say(self, interaction: discord.ApplicationContext, message: str, guild_id: str, channel_id: str, reply_message_id: str = None):
        try:
            guild: discord.Guild = await self.bot.fetch_guild(int(guild_id))
        except discord.Forbidden:
            await interaction.response.send_message("Guild not found", ephemeral=True)
            return
        try:
            channel = await guild.fetch_channel(int(channel_id))
        except discord.NotFound:
            await interaction.response.send_message("Channel not found", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
            return
        if reply_message_id:
            try:
                reply_message = await channel.fetch_message(int(reply_message_id))
            except discord.NotFound:
                await interaction.response.send_message("Message not found", ephemeral=True)
                return
            except discord.Forbidden:
                await interaction.response.send_message("Bot does not have permission to reply to messages", ephemeral=True)
                return
            try:
                m = await reply_message.reply(message)
            except discord.Forbidden:
                await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
                return
        else:
            try:
                m = await channel.send(message)
            except discord.Forbidden:
                await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
                return
        await interaction.response.send_message(f"Message sent: {m.jump_url}")

    @commands.slash_command(name="copy", description="you dont wanna know", guild_ids=[906909577394663484])
    @commands.is_owner()
    async def copy(self, interaction: discord.ApplicationContext, guild_id: str, channel_id: str):
        # copy user messages from one channel to another and timeout after 2 minutes
        try:
            guild: discord.Guild = await self.bot.fetch_guild(int(guild_id))
        except discord.Forbidden:
            await interaction.response.send_message("Error while fetching guild, try again later.", ephemeral=True)
            return
        try:
            channel = await guild.fetch_channel(int(channel_id))
        except discord.NotFound:
            await interaction.response.send_message("Channel not found", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
            return
        await interaction.response.send_message("Copy started, timeout in 2 minutes")

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        self.copy_message = True
        while self.copy_message:
            try:
                message = await self.bot.wait_for("message", check=check, timeout=120)
            except asyncio.TimeoutError:
                await interaction.followup.send("Copy timed out", ephemeral=True)
                return
            try:
                if "|" in message.content:
                    content, reply_message_id = message.content.rsplit("|", 1)
                    reply_message_id = reply_message_id.strip()
                    if not reply_message_id.isdigit():
                        await channel.send(message.content)
                        continue
                    try:
                        reply_message = await channel.fetch_message(int(reply_message_id))
                    except discord.NotFound:
                        await interaction.followup.send("Message not found", ephemeral=True)
                        return
                    except discord.Forbidden:
                        await interaction.followup.send("Bot does not have permission to reply to messages", ephemeral=True)
                        return
                    if self.copy_message:
                        await channel.send(content, reference=reply_message)
                else:
                    if self.copy_message:
                        await channel.send(message.content)
            except discord.Forbidden:
                await interaction.followup.send("Bot does not have permission to send messages in that channel", ephemeral=True)
                return

    @commands.slash_command(name="stop", description="stop the copy command", guild_ids=[906909577394663484])
    @commands.is_owner()
    async def stop(self, interaction: discord.ApplicationContext):
        if self.copy_message:
            self.copy_message = False
            await interaction.response.send_message("Copy stopped")
        else:
            await interaction.response.send_message("Copy is not running", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guildid = str(member.guild.id)
        if guildid not in welcomedict:
            return
        if "joinDM" in welcomedict[guildid]:
            try:
                await member.send(welcomedict[guildid]["joinDM"])
            except:
                pass
        if "welcomeChannel" in welcomedict[guildid] and "welcomeMessage" in welcomedict[guildid]:
            channel = await self.bot.fetch_channel(welcomedict[str(member.guild.id)]["welcomeChannel"])
            try:
                await channel.send(welcomedict[str(member.guild.id)]["welcomeMessage"].replace("{user}", member.mention).replace("{server}", member.guild.name))
            except:
                pass

    @commands.slash_command(name="welcome", description="set the welcome message and channel")
    @commands.has_permissions(manage_guild=True)
    async def welcome(
        self,
        interaction: discord.ApplicationContext,
        channel: discord.TextChannel = "",
        *,
        message: str = "Hello there,{user}\nWelcome to {server}\nGet yourself some roles\nHave a great time here in the server!",
    ):
        if str(interaction.guild.id) not in welcomedict:
            serverDB.insert_one({"_id": str(interaction.guild.id), "welcomeChannel": channel.id, "welcomeMessage": message, "joinDM": ""})
            welcomedict[str(interaction.guild.id)] = {"welcomeChannel": channel.id, "welcomeMessage": message, "joinDM": ""}
        else:
            serverDB.update_one({"_id": str(interaction.guild.id)}, {"$set": {"welcomeChannel": channel.id, "welcomeMessage": message}})

        welcomedict[str(interaction.guild.id)]["welcomeChannel"] = channel.id
        welcomedict[str(interaction.guild.id)]["welcomeMessage"] = message

        await interaction.response.send_message(f"Welcome message set to {message} in {channel.mention}")

    @commands.slash_command(name="joindm", description="set the join dm message")
    @commands.has_permissions(manage_guild=True)
    async def joindm(self, interaction: discord.ApplicationContext, *, message = ""):
        if str(interaction.guild.id) not in welcomedict:
            serverDB.insert_one({"_id": str(interaction.guild.id), "welcomeChannel": "", "welcomeMessage": "", "joinDM": message})
            welcomedict[str(interaction.guild.id)] = {"welcomeChannel": "", "welcomeMessage": "", "joinDM": message}

        else:
            serverDB.update_one({"_id": str(interaction.guild.id)}, {"$set": {"joinDM": message}})

        welcomedict[str(interaction.guild.id)]["joinDM"] = message

        await interaction.response.send_message(f"Join DM message set to `{message}`")

    @commands.slash_command(name='whosplaying', description='Get a list of all users playing a certain game')
    @discord.option(name='game', description='The game to search for', required=True, autocomplete=get_game)
    async def teammates(self, interaction: discord.ApplicationContext, game: str):
        guild = interaction.guild
        members = {}
        icon = None
        for member in guild.members:
            if not member.activities:
                continue
            for activity in member.activities:
                if not activity.type == discord.ActivityType.playing:
                    continue
                if activity.name.lower() == game.lower():
                    members[member] = activity.start
                    if not icon:
                        try:
                            icon = activity.small_image_url or activity.large_image_url
                        except:
                            pass
                    game = activity.name
                    
        if len(members) == 0:
            embed = discord.Embed(title=f"No users playing {game}", color=discord.Color.red())
            embed.set_thumbnail(url = 'https://em-content.zobj.net/thumbs/160/apple/21/pensive-face_1f614.png')
            embed.set_footer(text='Try again later')
            embed.timestamp = datetime.datetime.utcnow()
            await interaction.response.send_message(embed=embed)
            return
        embed = discord.Embed(title=f"Users playing {game}", color=discord.Color.random())
        embed.set_footer(text=f"Total users: {len(members)}")
        if icon:
            embed.set_thumbnail(url=icon)
        embed.timestamp = datetime.datetime.utcnow()
        for member in members:
            if members[member]:
                value = f"Started: <t:{int(members[member].timestamp())}:R>"
            else:
                value = "Started: Unknown"
            embed.add_field(name=f"{member.name}", value=value)
        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))
    print("Misc cog loaded")
