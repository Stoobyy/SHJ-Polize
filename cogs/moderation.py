import asyncio
import re
import os
from datetime import datetime, timedelta, timezone
import random

import discord
from discord.ext import commands


devs = (499112914578309120, 700195735689494558)
kicklist = [
    "https://i.pinimg.com/originals/44/6f/49/446f49e675e38e1bb10d226f12519092.gif",
    "https://media.tenor.com/D5OWYMGcAzAAAAAM/escondido-catedrales.gif",
    "https://media.tenor.com/5JmSgyYNVO0AAAAC/asdf-movie.gif",
]
# banlist = ['https://media3.giphy.com/media/ighlFxquiER8dGR56z/giphy.gif', 'https://steamuserimages-a.akamaihd.net/ugc/850474043001739503/8C513A4D4103B545AEA5594BFC4D31B5E5389B46/?imw=1024&imh=882&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true']


class HierarchyMember(commands.MemberConverter):
    """
    A member converter that respects Discord's role hierarchy system.
    """

    async def convert(self, ctx, arg):
        member = await super().convert(ctx, arg)

        can_do_action = ctx.author == ctx.guild.owner or ctx.author.top_role > member.top_role or ctx.author.id in devs
        if not can_do_action:
            raise commands.BadArgument("Role hierarchy prevents you from doing this.")
        return member


class HackMember(HierarchyMember):
    """
    A member converter that also allows arbitrary IDs to be passed.
    """

    async def convert(self, ctx, arg):
        try:
            member = await super().convert(ctx, arg)
            return member.id
        except commands.BadArgument:
            try:
                return int(arg)
            except ValueError:
                raise commands.BadArgument(f'"{arg}" is not a valid member or ID.')


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.check_any(commands.has_permissions(kick_members=True), commands.is_owner())
    async def kick(self, ctx, member: HierarchyMember, *, reason: str = None):
        await member.kick(reason=reason)
        embed = discord.Embed(title="Mod Action", description=f"{member.mention} has been kicked for `{reason}`", color=15548997)
        embed.timestamp = datetime.now()
        embed.set_image(url=random.choice(kicklist))
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def ban(self, ctx, user: HackMember, *, reason: str = None):
        user = await self.bot.fetch_user(user)
        await ctx.guild.ban(user, reason=reason)
        embed = discord.Embed(title="Banned", description=f"{user.mention} has been banned for `{reason}`", color=15548997)
        embed.timestamp = datetime.now()
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def unban(self, ctx, user: int, *, reason: str = None):
        user = await self.bot.fetch_user(user)
        await ctx.guild.unban(user, reason=reason)
        embed = discord.Embed(title="Unbanned", description=f"{user.mention} has been unbanned", color=2067276)
        embed.timestamp = datetime.now()
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.slash_command(name="kick", description="Kick a member")
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.check_any(commands.has_permissions(kick_members=True), commands.is_owner())
    async def _kick(self, ctx, member: HierarchyMember, *, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        embed = discord.Embed(title="Mod Action", description=f"{member.mention} has been kicked for `{reason}`", color=15548997)
        embed.timestamp = datetime.now()
        embed.set_image(url=random.choice(kicklist))
        await ctx.send(embed=embed)
        await ctx.respond("Kicked", ephemeral=True)

    @commands.slash_command(name="ban", description="Ban a user")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def _ban(self, ctx, user: HackMember, *, reason: str = "No reason provided"):
        user = await self.bot.fetch_user(user)
        await ctx.guild.ban(user, reason=reason)
        embed = discord.Embed(title="Mod Action", description=f"{user.mention} has been banned for `{reason}`", color=15548997)
        embed.timestamp = datetime.now()
        # url = random.choice(banlist)
        # embed.set_image(url= url) if url.endswith('gif') else embed.set_thumbnail(url=url)
        await ctx.send(embed=embed)
        await ctx.respond("Banned", ephemeral=True)

    @commands.slash_command(name="unban", description="Unban a user")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def _unban(self, ctx, user: str, *, reason: str = "No reason provided"):
        user = await self.bot.fetch_user(int(user))
        await ctx.guild.unban(user, reason=reason)
        embed = discord.Embed(title="Mod Action", description=f"{user.mention} has been unbanned", color=2067276)
        embed.timestamp = datetime.now()
        await ctx.send(embed=embed)
        await ctx.respond("Unbanned", ephemeral=True)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send("Purged {} message{}".format(amount, "s" if amount != 1 else ""), delete_after=5)


def setup(bot):
    bot.add_cog(Moderation(bot))
    print("Moderation Cog Loaded")
