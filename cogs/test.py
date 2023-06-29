import discord
from discord.ext import commands
import datetime
from datetime import timedelta
import json
from ext.topgg import votecheck
from ext.database import db


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.check(votecheck)
    async def secret(self, ctx):
        await ctx.reply("||thanks for voting||")


def setup(bot: commands.Bot):
    bot.add_cog(Test(bot))
    print("Test cog loaded")
