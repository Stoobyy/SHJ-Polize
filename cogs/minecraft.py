import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from discord.commands import SlashCommandGroup
import asyncio
import requests
from mojang import MojangAPI

class Mc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    mc = SlashCommandGroup(name="mmc", description="Minecraft commands")

    @mc.command(name="skin", description="mnecraft skind")
    @discord.option(name="username", type=str, description="Username", required=True)
    async def skin(self, ctx, username):
        id=ctx.author.id
        embed=discord.Embed()
        embed.add_field(name='No Username Provided!',value='Please provide a username or register your account by running `>register {username} {SkyblockProfile}`\nIf you don\'t play Skyblock, you can set the SkyblockProfile to None.')
        await ctx.send(embed=embed)
        uuid=MojangAPI.get_uuid(username)
        name=MojangAPI.get_username(uuid)
        if name==None:
            await ctx.send(f'<:Mike:882149622561243137> {username} is not a valid username.')
            return
        embed=discord.Embed(title=f'{name}\'s skin',description=f'[Click here for skin](https://crafatar.com/skins/{uuid})',colour=15105570)
        embed.set_image(url=f'https://visage.surgeplay.com/full/{uuid}?width=177&height=288')
        embed.set_thumbnail(url=f'https://visage.surgeplay.com//face/{uuid}')
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=f'{ctx.author.avatar}')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Mc(bot))
    print("mc cog loaded")