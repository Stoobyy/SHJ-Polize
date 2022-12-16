import discord
from discord.ext import commands
import datetime
from datetime import timedelta


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    def dxb_status():
        return self.client.get_guild(723259592800206940).get_member(763642116953604098).status == discord.Status.online
    
    @commands.Cog.listener()
    async def on_member_join(member):
        if dxb_status():
            return
        channel = await self.client.fetch_channel(734011317798830111)
        await channel.send(f'Hello there,{member.mention}\nGet yourself some roles from <#767320632663998494>\nHave a great time here in the server!')


def setup(client):
    client.add_cog(Moderation(client))
    print("Moderation cog loaded")