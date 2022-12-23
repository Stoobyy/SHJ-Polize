import discord
from discord.ext import commands
import topgg



class Topgg(commands.Cog):
    def __init__(self, client : commands.Bot):
        self.client = client

    @topgg.endpoint("/dblwebhook", topgg.WebhookType.BOT)
    async def on_vote(self, vote_data: topgg.BotVoteData):
        if vote_data.type == "test":
            print(f"Received a test vote by:\n{vote_data.user}")
        else:
            print(f"Received a vote by:\n{vote_data.user}")
            user = await self.client.fetch_user(vote_data.user)
            await user.send("Thanks for voting for SHJ-Polize on top.gg!")
            

def setup(client):
    client.add_cog(Topgg(client))
    print("Topgg cog loaded")


