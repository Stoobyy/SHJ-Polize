import asyncio
import re
import os
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands


devs = (499112914578309120, 700195735689494558)

class HierarchyMember(commands.MemberConverter):
    """
    A member converter that respects Discord's role hierarchy system.
    """
    async def convert(self, ctx, arg):
        member = await super().convert(ctx, arg)

        can_do_action = (ctx.author == ctx.guild.owner or
                         ctx.author.top_role > member.top_role or 
                         ctx.author.id in devs)
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
    """
    Moderation commands to manage your server.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.check_any(commands.has_permissions(kick_members=True), commands.is_owner())
    async def kick(self, ctx, member: HierarchyMember, *, reason: str = None, ephemeral: bool = False):
        """
        Kick a member.
        """
        await member.kick(reason=reason)
        embed = discord.Embed(title="Kicked", description=f"{member.mention} has been kicked from {ctx.guild.name}", color=15548997)
        await ctx.send(embed=embed, ephemeral=ephemeral)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def ban(self, ctx, user: HackMember, *, reason: str = None, ephemeral: bool = False):
        """
        Ban a user.

        You can also ban users who are not in your server by passing in their ID as the argument.
        """
        user = await self.bot.fetch_user(user)
        await ctx.guild.ban(user, reason=reason)
        embed = discord.Embed(title="Banned", description=f"{user.mention} has been banned from {ctx.guild.name}", color=15548997)
        await ctx.send(embed=embed, ephemeral=ephemeral)


    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner())
    async def unban(self, ctx, user: int, *, reason: str = None):
        """
        Unban a user.
        """
        user = await self.bot.fetch_user(user)
        await ctx.guild.unban(user, reason=reason)
        embed = discord.Embed(title="Unbanned", description=f"{user.mention} has been unbanned from {ctx.guild.name}", color=2067276)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
    print("Moderation Cog Loaded")