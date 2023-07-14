import discord
from discord.ext import commands
import datetime
from datetime import timedelta


class Funfish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def dxb_status(self):
        return self.bot.get_guild(723259592800206940).get_member(763642116953604098).status == discord.Status.online
    
    @commands.command(hidden=True)
    async def serverinfo(self, ctx):
        if ctx.guild.id != 723259592800206940:
            return
        embed = discord.Embed(title="FishyMC", description="Version = `1.19 `\nIP = `funfishmc.aternos.me`", colour=2123412)
        embedd = discord.Embed(
            title="Rules",
            description="""1. Swearing is allowed, but don’t get personal.
    2. Stealing from people isnt allowed. If you want something, work for it.
    3. Pranks are allowed, as long as it isn’t griefing. If something gets griefed, it’s your responsibility to fix it.
    4. Cheats are strictly not allowed. Any player found to log on with any kind of hack, this includes hacked clients and mods, will face severe punishments.
    5. Spamming in chats or leaking personal information in chats is stictly not allowed.
    Players found to break these rules are subject to severe punishments. These punishments include chat mutes, temporary bans, permanant bans, etc. Punishment will depend on the severity of the offense commited.""",
            colour=1243903,
        )
        await ctx.send(content="FishyMC V(Lost track) is finally live.", embed=embed)
        await ctx.send(embed=embedd)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if ctx.guild.id != 723259592800206940:
            return
        if self.dxb_status():
            return
        channel = await self.bot.fetch_channel(734011317798830111)
        await channel.send(f'Hello there,{member.mention}\nGet yourself some roles from <#767320632663998494>\nHave a great time here in the server!')


def setup(bot):
    bot.add_cog(Funfish(bot))
    print("Funfish cog loaded")
