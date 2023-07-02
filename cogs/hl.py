import os
from datetime import datetime, timedelta, timezone

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

from ext.database import db

highlightdb = db["hl"]

tzone = timezone(timedelta(hours=4))

last = {}

hllist = {}


class Highlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        data = highlightdb.find()
        for i in data:
            hllist[i["_id"]] = i["hl"]

    @commands.Cog.listener("on_message")
    async def hl_check(self, message):
        if message.author.bot or not message.guild:
            return
        guildid = message.guild.id
        current_time = datetime.now(tzone)
        unix_timestamp = current_time.timestamp()
        if guildid in last:
            last[guildid][str(message.author.id)] = unix_timestamp
        else:
            last[guildid] = {str(message.author.id): unix_timestamp}

        if guildid in hllist:
            guildhl = hllist[guildid]
        else:
            return

        users = []

        for user in guildhl:
            for msg in guildhl[user]:
                if user in users:
                    continue
                flag = False
                if " " in msg:
                    if msg.upper() in message.content.upper():
                        flag = True
                else:
                    for i in message.content.upper().split():
                        if i.startswith(msg.upper()):
                            flag = True
                if flag:
                    users.append(user)
                    message1 = []
                    async for i in message.channel.history(limit=5):
                        timee = i.created_at
                        message1.append(f'**[{timee.strftime("%H:%M:%S")}] {i.author.name}**: {i.content}\n')
                    message1.reverse()
                    embed = discord.Embed(
                        title=f"**{msg}**",
                        description=f'{"".join(message1)}\n**Source Message**\n[Jump to message]({message.jump_url})',
                        color=1752220,
                    )
                    embed.set_footer(text=f"Message ID: {message.id} | Author ID: {message.author.id}")
                    member = message.guild.get_member(int(str(user)))
                    if member is None or not message.channel.permissions_for(member).read_messages:
                        return
                    timee = datetime.now(tzone).timestamp()
                    lastt = last[guildid][user] if user in last[guildid] else 0
                    if lastt == 0 or timee - lastt > 300:
                        try:
                            await member.send(
                                f'In **{message.guild.name}** {message.channel.mention}, you were mentioned with highlight word "{msg}"', embed=embed
                            )
                        except discord.Forbidden:
                            pass

    hl = SlashCommandGroup(name="highlight", description="Highlight commands")

    @hl.command(name="list", description="List all highlights")
    async def hl_list(self, ctx):
        guildid = ctx.guild.id
        if guildid in hllist:
            guildhl = hllist[guildid]
        else:
            ghl = highlightdb.find_one({"_id": guildid})
            if ghl is None:
                highlightdb.insert_one({"_id": guildid, "hl": {}})
                ghl = highlightdb.find_one({"_id": guildid})
            guildhl = ghl["hl"]
            hllist[guildid] = guildhl

        if str(ctx.author.id) not in guildhl:
            embed = discord.Embed(title="Highlight List", description=f"You currently have no highlight words\nRun /hl add [word] to add some", color=1752220)
            await ctx.respond(embed=embed)
        else:
            if len(guildhl[str(ctx.author.id)]) == 0:
                embed = discord.Embed(
                    title="Highlight List", description=f"You currently have no highlight words\nRun /hl add [word] to add some", color=1752220
                )
                await ctx.respond(embed=embed)
            else:
                str1 = ""
                for i in guildhl[str(ctx.author.id)]:
                    str1 += f"{i}\n"
                embed = discord.Embed(title="You're currently tracking the following words", description=str1, color=1752220)
                await ctx.respond(embed=embed)

    @hl.command(name="add", description="Add a highlight word")
    @discord.option(name="word", required=True)
    async def hl_add(self, ctx, word):
        guildid = ctx.guild.id
        if guildid in hllist:
            guildhl = hllist[guildid]
        else:
            ghl = highlightdb.find_one({"_id": guildid})
            if ghl is None:
                highlightdb.insert_one({"_id": guildid, "hl": {}})
                ghl = highlightdb.find_one({"_id": guildid})
            guildhl = ghl["hl"]
            hllist[guildid] = guildhl

        if str(ctx.author.id) in guildhl:
            if word in guildhl[str(ctx.author.id)]:
                await ctx.respond(f"{word} is already in your highlight list")
            else:
                guildhl[str(ctx.author.id)].append(word)
                highlightdb.update_one({"_id": guildid}, {"$set": {"hl": guildhl}})
                hllist[guildid] = guildhl
                await ctx.respond(f"{word} has been added to your highlight list")
        else:
            guildhl[str(ctx.author.id)] = [word]
            highlightdb.update_one({"_id": guildid}, {"$set": {"hl": guildhl}})
            hllist[guildid] = guildhl
            await ctx.respond(f"{word} has been added to your highlight list")

    @hl.command(name="remove", description="Remove a highlight word")
    @discord.option(name="word", required=True)
    async def hl_remove(self, ctx, word):
        guildid = ctx.guild.id
        if guildid in hllist:
            guildhl = hllist[guildid]
        else:
            ghl = highlightdb.find_one({"_id": guildid})
            if ghl is None:
                highlightdb.insert_one({"_id": guildid, "hl": {}})
                ghl = highlightdb.find_one({"_id": guildid})
            guildhl = ghl["hl"]
            hllist[guildid] = guildhl

        if str(ctx.author.id) in guildhl:
            if word in guildhl[str(ctx.author.id)]:
                guildhl[str(ctx.author.id)].remove(word)
                highlightdb.update_one({"_id": guildid}, {"$set": {"hl": guildhl}})
                await ctx.respond(f"{word} has been removed from your highlight list")
                hllist[guildid] = guildhl
            else:
                await ctx.respond(f"{word} is not in your highlight list")
        else:
            await ctx.respond(f"You currently have no highlight words")


def setup(bot):
    bot.add_cog(Highlight(bot))
    print("Highlight cog loaded")
