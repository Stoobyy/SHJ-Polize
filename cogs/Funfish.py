import discord
from discord.ext import commands, tasks
import datetime
from datetime import datetime, timedelta, timezone


class Funfish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timestamp = 0
        self.bump_check.start()
    
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
        if member.guild.id != 723259592800206940:
            return
        if self.dxb_status():
            return
        try:
            channel = await self.bot.fetch_channel(734011317798830111)
            await channel.send(f'Hello there,{member.mention}\nGet yourself some roles from <#767320632663998494>\nHave a great time here in the server!')
        except error as e:
            raise e
    
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.guild.id != 723259592800206940:
            return
        if message.author.id != 302050872383242240:
            return
        if message.embeds:
            if message.embeds[0].description.startswith("Bump done"):
                self.timestamp = message.created_at.timestamp()
                print(self.timestamp, "bump timestamp")
                print(datetime.now().timestamp(), "current timestamp\n")
    
    @tasks.loop(seconds=60) 
    async def bump_check(self):
        if self.timestamp == 0:
            return
        if self.dxb_status():
            return
        if datetime.now().timestamp() - self.timestamp > 7200:
            print("trying to bump remind")
            try:
                channel = await self.bot.fetch_channel(757581111512530954) 
                await channel.send("<@&773548077024804874> the server needs your help. Bump it please")
                print("bump reminder successful ")
            except error as e:
                raise e
    
    @bump_check.before_loop
    async def before_my_task(self): 
        await self.bot.wait_until_ready()
    
def setup(bot):
    bot.add_cog(Funfish(bot))
    print("Funfish cog loaded")
