import os
from datetime import datetime, timedelta
from ext.topgg import VoteCheckError
from ext.database import db

startup_time = datetime.now().timestamp()

import discord
from discord.ext import commands, bridge
from pymongo import MongoClient


collection = db["prefixes"]

prefixes = {}


async def get_prefix(bot, message):
    prefix = prefixes.get(str(message.guild.id if message.guild else None), ">")
    return commands.when_mentioned_or(prefix)(bot, message)

intents = discord.Intents.default()
intents.members = True
# intents.presences = True
intents.message_content = True

bot = bridge.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

for cog in os.listdir("./cogs"):
    if cog.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{cog[:-3]}", store=False)
        except Exception as e:
            print(f"Failed to load {cog[:-3]}")
            print(e)

bot.load_extension("jishaku")

class HelpDropdown(discord.ui.Select):
    def __init__(self, embeds):
        self.embeds = embeds
        options = []
        for i in embeds:
            options.append(discord.SelectOption(label=i.title, value=i.title))
        super().__init__(placeholder="Choose a category", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        for i in self.embeds:
            if i.title == self.values[0]:
                await interaction.response.edit_message(embed=i, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, embeds):
        self.embeds = embeds
        super().__init__(HelpDropdown(embeds),timeout=60, disable_on_timeout=True)
    
    async def on_timeout(self):
        self.disable_all_items()
        message = self._message or self.parent
        try:
            await message.edit(view=self)
        except discord.NotFound:
            pass
    

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    for document in collection.find():
        prefixes[document["_id"]] = document["prefix"]
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name="with fishes"))


@bot.event
async def on_message(message):
    prefix = prefixes.get(str(message.guild.id if message.guild else None), ">")
    if message.content == bot.user.mention:
        await message.reply(f"My prefix is `{prefix}`")
    await bot.process_commands(message)

@bot.bridge_command(name="help", description="Get help on how to use the bot")
async def help(ctx: discord.ApplicationContext):
    embed1 = discord.Embed(title="General", color=discord.Color.blurple())
    embed1.add_field(name="`/help`", value="Get help on how to use the bot")
    embed1.add_field(name="`[/]ping`", value="Get the bot's latency")
    embed1.add_field(name="`[/]about`", value="Get info about the bot")
    embed1.add_field(name="`[/]vote`", value="Vote for the bot")
    embed1.add_field(name="`status`", value="Get the bot's uptime")
    embed1.add_field(name="`prefix`", value="Change the bot's prefix")

    embed2 = discord.Embed(title="Moderation", color=discord.Color.blurple())
    embed2.add_field(name="`[/]kick`", value="Kick a member")
    embed2.add_field(name="`[/]ban`", value="Ban a member")
    embed2.add_field(name="`[/]unban`", value="Unban a member")
    embed2.add_field(name="`purge`", value="Purge messages")

    embed3 = discord.Embed(title="Misc", color=discord.Color.blurple())
    embed3.add_field(name="`[/]spotify`", value="Get info about a spotify track a user is listening to")
    embed3.add_field(name="`snowflake`", value="Get time difference between a discord snowflake and now or another snowflake")
    embed3.add_field(name="`/welcome`", value="Set a welcome channel and message")
    embed3.add_field(name="`/joindm`", value="Set a join dm message")

    embed4 = discord.Embed(title="Snipe", color=discord.Color.blurple())
    embed4.add_field(name="`[/]snipe`", value="Snipe a deleted message")
    embed4.add_field(name="`dmsnipe`", value="Snipe a deleted message in dms")
    embed4.add_field(name="`[/]editsnipe`", value="Snipe an edited message")
    embed4.add_field(name="`dmesnipe`", value="Snipe an edited message in dms")
    embed4.add_field(name="`delete`", value="Delete a snipe")

    embed5 = discord.Embed(title="Highlight", color=discord.Color.blurple())
    embed5.add_field(name="`/highlight add`", value="Add a highlight word")
    embed5.add_field(name="`/highlight list`", value="List all highlight words")
    embed5.add_field(name="`/highlight remove`", value="Remove a highlight word")

    embed6 = discord.Embed(title="Minecraft", color=discord.Color.blurple())
    embed6.add_field(name="`server`", value="Get info about a minecraft server")
    embed6.add_field(name="`[/]skin`", value="Get a minecraft user's skin")
    embed6.add_field(name="`[/]cape`", value="Get a minecraft user's cape")

    embed7 = discord.Embed(title="Ez", color=discord.Color.blurple())
    embed7.add_field(name="`/ez blacklist`", value="blacklist a channel or user")
    embed7.add_field(name="`/ez info`", value="list blacklisted channels and users and shows deleteafter")
    embed7.add_field(name="`/ez deleteafter`", value="Set the deleteafter time for ez messages in channels and server")
    embed7.add_field(name="`/ez disable`", value="disable serverwide blacklist")

    embeds = [embed1, embed2, embed3, embed4, embed5, embed6, embed7]

    await ctx.respond(embed=embed1, view=HelpView(embeds))

@bot.bridge_command(name="ping", description="Get the bot's latency")
async def ping(ctx):
    await ctx.respond(f"{bot.latency * 1000 : .2f}ms")


@bot.bridge_command(name="prefix", description="Change the bot's prefix")
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def prefix(ctx, prefix: str):
    if len(prefix) > 5:
        await ctx.respond("Prefix cannot be longer than 5 characters", ephemeral=True)
        return
    if prefix == prefixes.get(str(ctx.guild.id), ">"):
        await ctx.respond("Prefix is already set to that", ephemeral=True)
        return
    if str(ctx.guild.id) in prefixes:
        collection.update_one({"_id": str(ctx.guild.id)}, {"$set": {"prefix": prefix}})
    else:
        collection.insert_one({"_id": str(ctx.guild.id), "prefix": prefix})
    prefixes[str(ctx.guild.id)] = prefix
    await ctx.respond(f"Prefix set to `{prefix}`")


@bot.bridge_command()
async def about(ctx: discord.ApplicationContext):
    embed = discord.Embed(title=f"About SHJ Polize", color=discord.Color.blurple(), url="https://top.gg/bot/969663219570462790")
    info = await ctx.bot.application_info()
    owners = [ctx.bot.get_user(i.id) for i in info.team.members]
    embed.description = "I am made by `{}` and `{}`".format(owners[0], owners[1])
    embed.add_field(name="Vote for me", value="[Click Here](https://top.gg/bot/969663219570462790/vote)")
    embed.add_field(name="Source Code", value="[Click Here](https://github.com/Stoobyy/SHJ-Polize)")
    embed.add_field(name="Support sever", value="[Click Here](https://discord.gg/z62AMMKVnX)")
    embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    await ctx.respond(embed=embed)

@bot.bridge_command(name="vote", description="Vote for the bot")
async def vote(ctx):
    await ctx.respond("https://top.gg/bot/969663219570462790/vote")

@bot.command(hidden=True)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension}")


@bot.command(hidden=True)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unloaded {extension}")


@bot.command(hidden=True)
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Reloaded {extension}")


@bot.command()
async def status(ctx):
    current_time = datetime.now().timestamp()
    time = current_time - startup_time
    time = str(timedelta(seconds=time))
    value = ""
    if "," in time:
        time = time.split(",")
        value += time[0] + " , "
        time = time[1]
    else:
        value += "0 days , "
    time = time.split(":")
    value += f"{time[0]} hours , {time[1]} minutes and {int(float(time[2]))} seconds"
    await ctx.reply(f"I have been online for `{value}`", mention_author=False)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.BotMissingPermissions):
        await ctx.reply("Bot is missing permissions to run that command", mention_author=False)
    elif isinstance(error, VoteCheckError):
        embed = discord.Embed(description= ' You need to vote for SHJ-Polize on top.gg to use this command!', color=discord.Color.blurple())
        embed.add_field(name="Vote for me", value="[Click Here](https://top.gg/bot/969663219570462790/vote)")
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/907118140473876490/1109813440723308564/17f5107688eeb6c6b07851e13a518046.png?width=608&height=608')
        await ctx.reply(embed=embed, mention_author=False)
    elif isinstance(
        error, (commands.errors.CheckAnyFailure, commands.errors.MissingAnyRole, commands.errors.MissingPermissions, commands.errors.NotOwner)
    ):
        await ctx.message.add_reaction("<a:nochamp:1021040710142668870>")
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.reply("Channel not found\n Either channel is not in guild or bot doesnt have access to that channel :(", mention_author=False)
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        pass
    elif isinstance(error, discord.errors.Forbidden):
        raise error
    else:
        await ctx.reply(f"`{type(error)}\n{error}`", mention_author=False)
        raise error


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.errors.BotMissingPermissions):
        await ctx.respond("Bot is missing permissions to run that command", ephemeral=True)
    elif isinstance(error, VoteCheckError):
        embed = discord.Embed(description= ' You need to vote for SHJ-Polize on top.gg to use this command!', color=discord.Color.blurple())
        embed.add_field(name="Vote for me", value="[Click Here](https://top.gg/bot/969663219570462790/vote)")
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/907118140473876490/1109813440723308564/17f5107688eeb6c6b07851e13a518046.png?width=608&height=608')
        await ctx.respond(embed=embed, ephemeral=True)
    elif isinstance(error, (commands.errors.CheckAnyFailure, commands.errors.MissingAnyRole, commands.errors.MissingPermissions)):
        await ctx.respond("<a:nochamp:1021040710142668870>", ephemeral=True)
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.respond("Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(")
    elif isinstance(error, discord.errors.Forbidden):
        raise error
    else:
        await ctx.respond(f"`{type(error)}\n{error}`", ephemeral=True)
        raise error

token = os.environ["TOKEN"]

bot.run(token)
