import os
from datetime import *


import discord
from discord.ext import commands

client = commands.Bot(command_prefix=commands.when_mentioned_or('>'), intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name='with fishes'))


@client.command()
async def ping(ctx):
    await ctx.send(f"{round(client.latency * 1000)}ms")




@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckAnyFailure or commands.errors.MissingAnyRole or commands.errors.MissingPermissions):
        await ctx.message.add_reaction('<a:nochamp:972351244700090408>')
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.reply('Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(')
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    else:
        await ctx.reply(f'{type(error)}\n{error}')
        raise error


@client.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckAnyFailure or commands.errors.MissingAnyRole or commands.errors.MissingPermissions):
        await ctx.respond('<a:nochamp:972351244700090408>', ephemeral=True)
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.respond('Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(')
    else:
        await ctx.respond(f'{type(error)}\n{error}', ephemeral=True)
        raise error


for cog in os.listdir('./cogs'):
    if cog.endswith('.py'):
        client.load_extension(f'cogs.{cog[:-3]}', store=False)


try:
    token = os.environ['TOKEN']
except KeyError:
    token = 'OTUyODM0MTMzMzg4ODI4NzMy.Yi7x8A.NJUC1KhacvrodNbMOQncj219lp0'
client.run(token)
