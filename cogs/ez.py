import asyncio
import os
import random
from datetime import *

import discord
import requests
from discord.commands import SlashCommandGroup
from discord.ext import commands

from ext.database import db

ezdb = db["ez"]

ez_list = [
    "Wait... This isn't what I typed!",
    "Anyone else really like Rick Astley?",
    "Hey helper, how play game?",
    "Sometimes I sing soppy, love songs in the car.",
    "I like long walks on the beach.",
    "Please go easy on me, this is my first time on discord!",
    "You're a great person! Do you want to chat?",
    "In my free time I like to watch cat videos on Youtube",
    "When I saw the witch with the potion, I knew there was trouble brewing.",
    "If the Minecraft world is infinite, how is the sun spinning around it?",
    "Hello everyone! I am an innocent person who loves chatting.",
    "Plz give me doggo memes!",
    "I heard you like Minecraft, so I built a computer in Minecraft in your Minecraft so you can Minecraft while you Minecraft",
    "Why can't the Ender Dragon read a book? Because he always starts at the End.",
    "Maybe we can have a rematch?",
    "I sometimes try to say bad things then this happens :(",
    "Behold, the great and powerful, my magnificent and almighty nemisis!",
    "Doin a bamboozle fren.",
    "Your comebacks are godly.",
    "What happens if I add chocolate milk to macaroni and cheese?",
    "Can you paint with all the colors of the wind",
    "Blue is greener than purple for sure",
    "I had something to say, then I forgot it.",
    "When nothing is right, go left.",
    "I need help, teach me how to play!",
    "Your personality shines brighter than the sun.",
    "You are very good at the game friend.",
    "I like pineapple on my pizza",
    "I like pasta, do you prefer nachos?",
    "I like fighting but you are truly better than me!",
    "I have really enjoyed playing with you! <3",
    "ILY <3",
    "Pineapple doesn't go on pizza!",
    "Lets be friends instead of fighting okay?",
]

bl_list = {}


class Ez(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        data = ezdb.find({})
        for i in data:
            bl_list[i["_id"]] = i

    @commands.Cog.listener("on_message")
    async def ez_webhook(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guildid = message.guild.id
        if guildid in bl_list:
            blacklist = bl_list[guildid]
        else:
            return

        if blacklist["serverwide_blacklist"] is True:
            return
        if message.channel.id in blacklist["channel_blacklist"] or message.author.id in blacklist["user_blacklist"]:
            return

        if "ez" in message.content.lower().split():
            try:
                hooks = await message.channel.webhooks()
                hook = discord.utils.get(hooks, name="ezz")
                if hook is None:
                    hook = await message.channel.create_webhook(name="ezz", avatar=None, reason=None)
                await message.delete()
            except discord.Forbidden:
                return
            data = {"content": random.choice(ez_list), "username": message.author.name, "avatar_url": message.author.avatar.url}
            hookurl = hook.url + "?wait=true"
            response = requests.post(hookurl, json=data)
            raw = response.json()
            channel = await self.bot.fetch_channel(int(raw["channel_id"]))
            messageid = await channel.fetch_message(int(raw["id"]))

            if str(message.channel.id) in blacklist["channel_deleteafter"]:
                time = blacklist["channel_deleteafter"][str(message.channel.id)]
            else:
                if blacklist["server_deleteafter"]:
                    time = blacklist["server_deleteafter"]
                else:
                    time = None
            if time != None:
                await asyncio.sleep(time)
                await messageid.delete()

    @commands.command(aliases=["eb"])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def blacklist(self, ctx, param: discord.Member or discord.TextChannel = None):
        if param is None:
            param = ctx.channel

        guildid = ctx.guild.id
        if guildid in bl_list:
            blacklist = bl_list[guildid]
        else:
            blacklist = ezdb.find_one({"_id": guildid})
            if blacklist is None:
                ezdb.insert_one(
                    {
                        "_id": guildid,
                        "channel_blacklist": [],
                        "user_blacklist": [],
                        "serverwide_blacklist": True,
                        "server_deleteafter": 0,
                        "channel_deleteafter": {},
                    }
                )
                blacklist = ezdb.find_one({"_id": guildid})
            bl_list[guildid] = blacklist

        if isinstance(param, discord.TextChannel):
            if param.id in blacklist["channel_blacklist"]:
                blacklist["channel_blacklist"].remove(param.id)
                ezdb.update_one({"_id": guildid}, {"$set": {"channel_blacklist": blacklist["channel_blacklist"]}})
                bl_list[guildid] = blacklist
                await ctx.message.add_reaction("👍")
                return
            blacklist["channel_blacklist"].append(param.id)
            ezdb.update_one({"_id": guildid}, {"$set": {"channel_blacklist": blacklist["channel_blacklist"]}})
            bl_list[guildid] = blacklist
            await ctx.message.add_reaction("👍")

        elif isinstance(param, discord.Member):
            if param.id in blacklist["user_blacklist"]:
                blacklist["user_blacklist"].remove(param.id)
                ezdb.update_one({"_id": guildid}, {"$set": {"user_blacklist": blacklist["user_blacklist"]}})
                bl_list[guildid] = blacklist
                await ctx.message.add_reaction("👍")
                return
            blacklist["user_blacklist"].append(param.id)
            ezdb.update_one({"_id": guildid}, {"$set": {"user_blacklist": blacklist["user_blacklist"]}})
            bl_list[guildid] = blacklist
            await ctx.message.add_reaction("👍")

    ez = SlashCommandGroup(name="ez", description="ez commands")

    @ez.command(name="blacklist", description="blacklist a channel or user")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    @discord.option(name="channel", type=discord.TextChannel, default=None, description="The channel to blacklist", required=False)
    @discord.option(name="user", type=discord.Member, default=None, description="The user to blacklist", required=False)
    async def ez_blacklist(self, ctx, channel: discord.TextChannel, user: discord.Member):
        guildid = ctx.guild.id
        if guildid in bl_list:
            blacklist = bl_list[guildid]
            
        else:
            blacklist = ezdb.find_one({"_id": guildid})
            if blacklist is None:
                ezdb.insert_one(
                    {
                        "_id": guildid,
                        "channel_blacklist": [],
                        "user_blacklist": [],
                        "serverwide_blacklist": True,
                        "server_deleteafter": 0,
                        "channel_deleteafter": {},
                    }
                )
                blacklist = ezdb.find_one({"_id": guildid})
            bl_list[guildid] = blacklist

        if isinstance(channel, discord.TextChannel):
            if channel.id in blacklist["channel_blacklist"]:
                blacklist["channel_blacklist"].remove(channel.id)
                ezdb.update_one({"_id": guildid}, {"$set": {"channel_blacklist": blacklist["channel_blacklist"]}})
                bl_list[guildid] = blacklist
                await ctx.respond(f"<#{channel.id}> is no longer blacklisted", ephemeral=True)
                return
            blacklist["channel_blacklist"].append(channel.id)
            ezdb.update_one({"_id": guildid}, {"$set": {"channel_blacklist": blacklist["channel_blacklist"]}})
            bl_list[guildid] = blacklist
            await ctx.respond(f"<#{channel.id}> is now blacklisted", ephemeral=True)
            return

        if isinstance(user, discord.Member):
            if user.id in blacklist["user_blacklist"]:
                blacklist["user_blacklist"].remove(user.id)
                ezdb.update_one({"_id": guildid}, {"$set": {"user_blacklist": blacklist["user_blacklist"]}})
                bl_list[guildid] = blacklist
                await ctx.respond(f"<@{user.id}> is no longer blacklisted", ephemeral=True)
                return
            blacklist["user_blacklist"].append(user.id)
            ezdb.update_one({"_id": guildid}, {"$set": {"user_blacklist": blacklist["user_blacklist"]}})
            bl_list[guildid] = blacklist
            await ctx.respond(f"<@{user.id}> is now blacklisted", ephemeral=True)
            return
        if channel is None and user is None:
            await ctx.respond(f"You need to specify a channel or user", ephemeral=True)
            return

    @ez.command(name="info", description="list blacklisted channels and users and shows deleteafter")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def ez_info(self, ctx):
        guildid = ctx.guild.id
        if guildid in bl_list:
            blacklist = bl_list[guildid]
        else:
            blacklist = ezdb.find_one({"_id": guildid})
            if blacklist is None:
                ezdb.insert_one(
                    {
                        "_id": guildid,
                        "channel_blacklist": [],
                        "user_blacklist": [],
                        "serverwide_blacklist": True,
                        "server_deleteafter": 0,
                        "channel_deleteafter": {},
                    }
                )
                blacklist = ezdb.find_one({"_id": guildid})
            bl_list[guildid] = blacklist

        embed = discord.Embed(title="Blacklist", description="Shows Blacklisted Channels and Users for ez message", colour=1752220)
        cb = "\n".join("<#{}>".format(x) for x in blacklist["channel_blacklist"])
        ub = "\n".join("<@{}>".format(x) for x in blacklist["user_blacklist"])
        embed.add_field(name="Serverwide blacklist", value=f"{blacklist['serverwide_blacklist']}")
        if len(blacklist["channel_blacklist"]) != 0:
            embed.add_field(name="Channels", value=cb, inline=False)
        if len(blacklist["user_blacklist"]) != 0:
            embed.add_field(name="Users", value=ub, inline=False)

        embed1 = discord.Embed(title="Deleteafter", description="Shows the current deleteafter", colour=1752220)
        if blacklist["server_deleteafter"] == 0:
            embed1.add_field(name="Serverwide deleteafter", value="Disabled", inline=False)
        else:
            embed1.add_field(name="Serverwide deleteafter", value=f"{blacklist['server_deleteafter']} seconds")
        if len(blacklist["channel_deleteafter"]) != 0:
            v = ""
            for x, j in blacklist["channel_deleteafter"].items():
                v += f"<#{x}> : {j} seconds\n"
            embed1.add_field(name="Channels", value=v, inline=False)
        await ctx.respond(embeds=[embed, embed1], ephemeral=True)

    @ez.command(name="disable", description="disable serverwide blacklist")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    @discord.option(name="disabled", type=bool, description="Disable serverwide blacklist", required=True)
    async def ez_disable(self, ctx, disabled):
        guildid = ctx.guild.id
        if guildid in bl_list:
            blacklist = bl_list[guildid]
        else:
            blacklist = ezdb.find_one({"_id": guildid})
            if blacklist is None:
                ezdb.insert_one(
                    {
                        "_id": guildid,
                        "channel_blacklist": [],
                        "user_blacklist": [],
                        "serverwide_blacklist": True,
                        "server_deleteafter": 0,
                        "channel_deleteafter": {},
                    }
                )
                blacklist = ezdb.find_one({"_id": guildid})
            bl_list[guildid] = blacklist

        sw = blacklist["serverwide_blacklist"]
        if sw is True:
            if disabled is True:
                await ctx.respond("Serverwide blacklist is already enabled", ephemeral=True)
                return
            else:
                blacklist["serverwide_blacklist"] = False
                ezdb.update_one({"_id": guildid}, {"$set": {"serverwide_blacklist": blacklist["serverwide_blacklist"]}})
                bl_list[guildid] = blacklist
                await ctx.respond(f"Serverwide blacklist is now disabled", ephemeral=True)
        else:
            if disabled is False:
                await ctx.respond("Serverwide blacklist is already disabled", ephemeral=True)
                return
            else:
                blacklist["serverwide_blacklist"] = True
                ezdb.update_one({"_id": guildid}, {"$set": {"serverwide_blacklist": blacklist["serverwide_blacklist"]}})
                bl_list[guildid] = blacklist
                await ctx.respond(f"Serverwide blacklist is now enabled", ephemeral=True)

    @ez.command(name="deleteafter", description="Set the deleteafter time for ez messages in channels and server")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    @discord.option(
        name="channel",
        type=discord.TextChannel,
        default=None,
        description="The channel to blacklist if empty changes server deleteafter",
        required=False,
    )
    @discord.option(name="time", type=int, default=None, description="The time in seconds", required=True)
    async def ez_deleteafter(self, ctx, channel: discord.TextChannel, time: int):
        guildid = ctx.guild.id
        if guildid in bl_list:
            blacklist = bl_list[guildid]
        else:
            blacklist = ezdb.find_one({"_id": guildid})
            if blacklist is None:
                ezdb.insert_one(
                    {
                        "_id": guildid,
                        "channel_blacklist": [],
                        "user_blacklist": [],
                        "serverwide_blacklist": True,
                        "server_deleteafter": 0,
                        "channel_deleteafter": {},
                    }
                )
                blacklist = ezdb.find_one({"_id": guildid})
            bl_list[guildid] = blacklist

        if channel is None:
            if time != None:
                blacklist["server_deleteafter"] = time
                ezdb.update_one({"_id": guildid}, {"$set": {"server_deleteafter": blacklist["server_deleteafter"]}})
                bl_list[guildid] = blacklist
                await ctx.respond(f"Server deleteafter set to {time} seconds", ephemeral=True)
            else:
                await ctx.respond("You need to specify a time", ephemeral=True)

        else:
            if time != None:
                if str(channel.id) in blacklist["channel_deleteafter"]:
                    blacklist["channel_deleteafter"][str(channel.id)] = time
                    ezdb.update_one({"_id": guildid}, {"$set": {"channel_deleteafter": blacklist["channel_deleteafter"]}})
                    bl_list[guildid] = blacklist
                    await ctx.respond(f"Deleteafter set to {time} seconds for <#{channel.id}>", ephemeral=True)
                else:
                    if blacklist["channel_deleteafter"] == {}:
                        blacklist["channel_deleteafter"] = {str(channel.id): time}
                    else:
                        blacklist["channel_deleteafter"][str(channel.id)] = time
                    ezdb.update_one({"_id": guildid}, {"$set": {"channel_deleteafter": blacklist["channel_deleteafter"]}})
                    bl_list[guildid] = blacklist
                    await ctx.respond(f"Deleteafter set to {time} seconds for <#{channel.id}>", ephemeral=True)
            else:
                blacklist["channel_deleteafter"].pop(str(channel.id))
                ezdb.update_one({"_id": guildid}, {"$set": {"channel_deleteafter": blacklist["channel_deleteafter"]}})
                bl_list[guildid] = blacklist
                await ctx.respond(f"Channel deleteafter removed", ephemeral=True)


def setup(bot):
    bot.add_cog(Ez(bot))
    print("Ez cog loaded")
