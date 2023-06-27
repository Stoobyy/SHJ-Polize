import discord
from discord.ext import commands
import os
import topgg
from .ext.topgg import manager, dblclient


def on_autopost_success():
    pass


def on_autopost_error(exception: Exception):
    print("Failed to post:", exception)


def stats(client: commands.Bot = topgg.data(commands.Bot)):
    return topgg.StatsWrapper(guild_count=len(client.guilds))

class Topgg(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.webhook_manager = manager.set_data(self.client)
        self.dblclient = dblclient.set_data(self.client)
        self.autoposter: topgg.AutoPoster = self.dblclient.autopost()
        self.autoposter.on_success(on_autopost_success).on_error(on_autopost_error).stats(stats).set_interval(1800)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.webhook_manager.is_running:
            await self.webhook_manager.start(port=5000)

        if not self.autoposter.is_running:
            self.autoposter.start()
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def votes(self, ctx):
        data = await self.dblclient.get_bot_votes()
        votes = ""
        for i in data:
            votes += f"{i.username}\n"
        await ctx.send(f"Votes : \n{votes}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def voted(self, ctx, user : discord.User):
        data = await self.dblclient.get_user_vote(user.id)
        await ctx.send(f"Username : {user}\nID : {user.id}\nHas voted : {data}")

def setup(bot):
    bot.add_cog(Topgg(bot))
    print("Topgg cog loaded")
