import discord
from discord.ext import commands
import datetime
from datetime import timedelta
class Test(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.slash_command()
    async def test(self, ctx):
        content = ""
        content += f"Owner: {ctx.bot.owner_id}\n"
        content += f"Owners: {ctx.bot.owner_ids}\n"
        c = await ctx.bot.is_owner(ctx.author)
        content += f"Is owner: {c}\n"
        content += f"Owner: {ctx.bot.owner_id}\n"
        content += f"Owners: {ctx.bot.owner_ids}\n"
        await ctx.respond(content)


    @commands.command()
    async def snowflake(self, ctx, snowflake, snowflake2=None):
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



def setup(client):
    client.add_cog(Test(client))
    print("Test cog loaded")