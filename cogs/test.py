import discord
from discord import app_commands
from discord.ext import commands
import datetime
from datetime import timedelta
class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="test", description="test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("test")

    @commands.command()
    async def snowflake(self, ctx : commands.Context, snowflake, snowflake2=None):
        s = discord.Object(id=snowflake)
        d : datetime.datetime = s.created_at.timestamp()
        if snowflake2:
            s2 = discord.Object(id=snowflake2)
            st : datetime.datetime = s2.created_at.timestamp()
        elif ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            st = msg.created_at.timestamp()
        else:
            st = datetime.datetime.now().timestamp()
        time = str(timedelta(seconds=st - d))
        value = ""
        if "," in time:
            time = time.split(",")
            value += time[0] + " , "
            time = time[1]
        time = time.split(":")
        if int(time[0]) != 0:
            value += time[0] + " hours, "
        if int(time[1]) != 0:
            value += time[1] + " minutes and "
        value += f"{float(time[2]) : .2f}" + " seconds"
        await ctx.reply(value, mention_author=False)



async def setup(bot):
    await bot.add_cog(Test(bot))
    print("Test cog loaded")