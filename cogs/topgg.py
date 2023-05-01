import discord
from discord.ext import commands
import os
import topgg


def on_autopost_success():
    print("Successfully posted!")


def on_autopost_error(exception: Exception):
    print("Failed to post:", exception)


def stats(client: commands.Bot = topgg.data(commands.Bot)):
    return topgg.StatsWrapper(guild_count=len(client.guilds))


@topgg.endpoint("/dblwebhook", topgg.WebhookType.BOT, auth=os.environ["BOT_AUTH"])
async def on_bot_vote(vote_data: topgg.BotVoteData, client: commands.Bot = topgg.data(commands.Bot)):
    user_id = vote_data.user
    try:
        user = await client.fetch_user(vote_data.user)
    except:
        user = None
    if vote_data.type == "test":
        print(f"Received a test vote by: {user} ({user_id})")
        try:
            await user.send("Test vote for SHJ-Polize was successful!")
        except:
            pass
    else:
        print(f"Received a vote by: {user} ({user_id})")
        try:
            await user.send("Thanks for voting for SHJ-Polize on top.gg!")
        except:
            pass


@topgg.endpoint("/dslwebhook", topgg.WebhookType.GUILD, auth=os.environ["SERVER_AUTH"])
async def on_guild_vote(vote_data: topgg.GuildVoteData, client: commands.Bot = topgg.data(commands.Bot)):
    user = await client.fetch_user(vote_data.user)
    guild: discord.Guild = await client.fetch_guild(vote_data.guild)
    if vote_data.type == "test":
        print(f"Received a test vote by: {user} ({vote_data.user}) for {guild.name}")
        try:
            await user.send(f"Test vote for {guild.name} was successful!")
        except:
            pass
    else:
        print(f"Received a vote by: {user} ({vote_data.user}) for {guild.name}")
        try:
            await user.send(f"Thanks for voting for {guild.name} on top.gg!")
        except:
            pass


class Topgg(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.webhook_manager = topgg.WebhookManager().set_data(self.client)
        self.webhook_manager.endpoint(on_bot_vote).endpoint(on_guild_vote)
        self.dblclient = topgg.DBLClient(os.environ["TOPGG_TOKEN"]).set_data(self.client).default_bot_id(self.client.user.id)
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

def setup(bot):
    bot.add_cog(Topgg(bot))
    print("Topgg cog loaded")
