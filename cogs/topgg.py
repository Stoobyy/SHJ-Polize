import discord
from discord.ext import commands, bridge
import os
import topgg
from ext.topgg import manager, dblclient


def on_autopost_success():
    pass


def on_autopost_error(exception: Exception):
    print("Failed to post:", exception)


def stats(client: bridge.Bot = topgg.data(bridge.Bot)):
    return topgg.StatsWrapper(guild_count=len(client.guilds))

class Topgg(commands.Cog):
    def __init__(self, client: bridge.Bot):
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
        embed = discord.Embed(title="Votes", description=f"Total votes : {len(data)}", color=discord.Color.green())
        votes = {}
        for i in data:
            votes[i.username] = votes[i.username]+1 if i.username in votes else 1
        top5 = sorted(votes.items(), key=lambda x: x[1], reverse=True)[:5]
        value = ""
        for i in top5:
            value += f"{i[0]} : {i[1]}\n"
        embed.add_field(name="Top 5 voters", value=value)
        embed.add_field(name="Last 5 voters", value="\n".join([i.username for i in data[:5]]))
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def voted(self, ctx, user : discord.User):
        data = await self.dblclient.get_user_vote(user.id)
        await ctx.send(f"Username : {user}\nID : {user.id}\nHas voted : {data}")

def setup(bot):
    bot.add_cog(Topgg(bot))
    print("Topgg cog loaded")
