import os
from datetime import *
startup_time = datetime.now().timestamp()

import discord
from discord.ext import commands

client = commands.Bot(command_prefix=commands.when_mentioned_or('>'), intents=discord.Intents.all())
roles = {0:734056569041322066, 3:756979356332589117, 5:734302084350083166, 10:734305511759151144, 25:757698628360863876, 35:734302384032841759, 50:734304865794392094, 65:808060262179012658, 70:734306269430677515}
startroles = [767016755809091654,767029516769689601,767017209389252658,767017558095429649,767017041319428107]



@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name='with fishes'))


@client.command()
async def ping(ctx):
    await ctx.reply(f"{client.latency * 1000 : .2f}ms", mention_author=False)

@client.slash_command()
async def ping(ctx):
    await ctx.respond(f"{client.latency * 1000 : .2f}ms")

@client.command(hidden=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension}')

@client.command(hidden=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension}')

@client.command(hidden=True)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded {extension}')

@client.command()
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
    
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.errors.CheckAnyFailure, commands.errors.MissingAnyRole, commands.errors.MissingPermissions, commands.errors.NotOwner)):
        await ctx.message.add_reaction('<a:nochamp:1021040710142668870>')
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.reply('Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(', mention_author=False)
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        pass
    else:
        await ctx.reply(f'{type(error)}\n{error}', mention_author=False)
        raise error


@client.event
async def on_application_command_error(ctx, error):
    if isinstance(error, (commands.errors.CheckAnyFailure, commands.errors.MissingAnyRole, commands.errors.MissingPermissions)):
        await ctx.respond('<a:nochamp:1021040710142668870>', ephemeral=True)
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.respond('Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(')
    else:
        await ctx.respond(f'{type(error)}\n{error}', ephemeral=True)
        raise error

@client.event
async def on_member_join(member):
    for role in startroles:
        await member.add_roles(get(member.guild.roles, id=role))
    channel = await client.fetch_channel(734011317798830111)
    await channel.send(f'Hello there,{member.mention}\nGet yourself some roles from <#767320632663998494>\nHave a great time here in the server!')



for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        client.load_extension(f'cogs.{cog[:-3]}', store=False)

client.load_extension('jishaku')

token = os.environ['TOKEN']

client.run(token)
