import os
from datetime import datetime, timedelta

startup_time = datetime.now().timestamp()

import discord
from discord.ext import commands
from pymongo import MongoClient

cluster = MongoClient(os.environ["MONGO"])
db = cluster["shj-polize"]
collection = db["prefixes"]

prefixes = {}


async def get_prefix(bot, message):
    prefix = prefixes.get(str(message.guild.id if message.guild else None), ">")
    return commands.when_mentioned_or(prefix)(bot, message)


bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())


@bot.event
async def on_ready():
    for cog in os.listdir("./cogs"):
        if cog.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{cog[:-3]}")
            except commands.errors.ExtensionAlreadyLoaded:
                pass
            except Exception as e:
                print(e.with_traceback(e.__traceback__))
    try:
        await bot.load_extension("jishaku")
    except:
        pass
    await bot.tree.sync()

    for document in collection.find():
        prefixes[document["_id"]] = document["prefix"]

    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name="with fishes"))

    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    prefix = prefixes.get(str(message.guild.id if message.guild else None), ">")
    if message.content == bot.user.mention:
        await message.reply(f"My prefix is `{prefix}`")
    await bot.process_commands(message)


@bot.command()
async def ping(ctx):
    await ctx.reply(f"{bot.latency * 1000 : .2f}ms", mention_author=False)


@bot.tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{bot.latency * 1000 : .2f}ms")


@bot.tree.command()
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def prefix(interaction: discord.Interaction, prefix: str):
    if len(prefix) > 5:
        await interaction.response.send_message("Prefix cannot be longer than 5 characters", ephemeral=True)
        return
    if prefix == prefixes.get(str(interaction.guild.id), ">"):
        await interaction.response.send_message("Prefix is already set to that", ephemeral=True)
        return
    if str(interaction.guild.id) in prefixes:
        collection.update_one({"_id": str(interaction.guild.id)}, {"$set": {"prefix": prefix}})
    else:
        collection.insert_one({"_id": str(interaction.guild.id), "prefix": prefix})
    prefixes[str(interaction.guild.id)] = prefix
    await interaction.response.send_message(f"Prefix set to `{prefix}`")


@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.guild_only()
async def prefix(ctx, prefix: str):
    if len(prefix) > 5:
        await ctx.reply("Prefix cannot be longer than 5 characters", mention_author=False)
        return
    if prefix == prefixes.get(str(ctx.guild.id), ">"):
        await ctx.reply("Prefix is already set to that", mention_author=False)
        return
    if str(ctx.guild.id) in prefixes:
        collection.update_one({"_id": str(ctx.guild.id)}, {"$set": {"prefix": prefix}})
    else:
        collection.insert_one({"_id": str(ctx.guild.id), "prefix": prefix})
    prefixes[str(ctx.guild.id)] = prefix
    await ctx.reply(f"Prefix set to `{prefix}`", mention_author=False)


@bot.tree.command()
async def about(interaction: discord.Interaction):
    embed = discord.Embed(title=f"About SHJ Polize", color=discord.Color.blurple(), url="https://top.gg/bot/969663219570462790")
    # info = await interaction.client.application_info()
    # owners = [interaction.client.get_user(i.id) for i in info.team.members]
    # embed.description = "I am made by `{}` and `{}`".format(owners[0], owners[1])
    embed.description = "I am made by `TrickyGamer#8188` and `Stooby#0215`"
    embed.add_field(name="Vote for me", value="[Click Here](https://top.gg/bot/969663219570462790/vote)")
    embed.add_field(name="Source Code", value="[Click Here](https://github.com/Stoobyy/SHJ-Polize)")
    embed.add_field(name="Support sever", value="[Click Here](https://discord.gg/z62AMMKVnX)")
    embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


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
    if isinstance(error, (commands.errors.CheckAnyFailure, commands.errors.MissingAnyRole, commands.errors.MissingPermissions, commands.errors.NotOwner)):
        await ctx.message.add_reaction("<a:nochamp:1021040710142668870>")
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.reply("Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(", mention_author=False)
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        pass
    else:
        await ctx.reply(f"`{type(error)}\n{error}`", mention_author=False)
        raise error


@bot.event
async def on_application_command_error(interaction: discord.Interaction, error):
    if isinstance(error, (commands.errors.CheckAnyFailure, commands.errors.MissingAnyRole, commands.errors.MissingPermissions)):
        await interaction.response.send_message("<a:nochamp:1021040710142668870>", ephemeral=True)
    elif isinstance(error, commands.errors.ChannelNotFound):
        await interaction.response.send_message("Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(")
    else:
        await interaction.response.send_message(f"`{type(error)}\n{error}`", ephemeral=True)
        raise error


token = os.environ['TOKEN']

bot.run(token)
