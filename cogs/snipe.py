import os
from datetime import datetime

import io

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks
from discord.ui import View

from ext.database import db

snipedb = db["snipe"]

deletemsg = {}
editmsg = {}

devs = (499112914578309120, 700195735689494558)
snipedata = {}


async def snipe_check(ctx):
    if str(ctx.guild.id) in snipedata:
        if ctx.author.id in snipedata[str(ctx.guild.id)]["users"]:
            return True
        else:
            for role in ctx.author.roles:
                if role.id in snipedata[str(ctx.guild.id)]["roles"]:
                    return True
    return False


class DeleteView(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx

    async def on_timeout(self):
        self.disable_all_items()
        message = self._message or self.parent
        try:
            await message.edit(view=self)
        except discord.NotFound:
            pass

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        s_m = False
        try:
            msg = deletemsg[str(interaction.channel.id)]
            msg["DontSnipe"] = True
            s_m = True
        except KeyError:
            pass

        message = self.ctx.message

        if message:
            user = message.author.id
        else:
            user = self.ctx.author.id

        if interaction.user.id == user or interaction.user.id in devs:
            await interaction.message.delete()
            if message:
                try:
                    await message.delete()
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass
        else:
            await interaction.response.send_message("You are not allowed to delete this message <a:nochamp:1021040710142668870>", ephemeral=True)

        if s_m == True:
            del msg["DontSnipe"]


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        d = snipedb.find({})
        for i in d:
            snipedata[i["_id"]] = i["data"]

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        # remove if you want to snipe nqn messages
        if message.author.discriminator == "0000":
            return

        content = message.content
        author = str(message.author)
        message_author_avatar = message.author.display_avatar.url
        channel = str(message.channel.id)
        timee = message.created_at or datetime.utcnow()

        if channel in deletemsg:
            if "DontSnipe" in deletemsg[channel]:
                return

        deletemsg[channel] = {"content": content, "author": author, "authorav": message_author_avatar, "time": timee}

        if message.attachments:
            attachment = message.attachments[0]
            if attachment.url.endswith((".png", ".jpg", ".jpeg", ".gif")):
                img = await attachment.read()
                deletemsg[channel]["img"] = img
                deletemsg[channel]["filename"] = attachment.filename
            else:
                deletemsg[channel]["attachment"] = attachment.url

    @commands.slash_command(name="snipe_whitelist", description="Whitelist a role or user to snipe messages (if left blank, shows the current whitelist)")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def snipe_whitelist(self, ctx: discord.ApplicationContext, role: discord.Role = None, user: discord.User = None):
        if str(ctx.guild.id) not in snipedata:
            snipedata[str(ctx.guild.id)] = {"roles": [], "users": []}
            snipedb.insert_one({"_id": str(ctx.guild.id), "data": snipedata[str(ctx.guild.id)]})
        if role is None and user is None:
            d = snipedata[str(ctx.guild.id)]
            embed = discord.Embed(title="Snipe Whitelist")
            r = "\n".join("<@&{}>".format(x) for x in d["roles"])
            u = "\n".join("<@{}>".format(x) for x in d["users"])
            if r == "":
                r = "None"
            if u == "":
                u = "None"
            embed.add_field(name="Roles", value=r)
            embed.add_field(name="Users", value=u)
            await ctx.respond(embed=embed)

        if role is not None:
            if role.id in snipedata[str(ctx.guild.id)]["roles"]:
                snipedata[str(ctx.guild.id)]["roles"].remove(role.id)
                snipedb.update_one({"_id": str(ctx.guild.id)}, {"$set": {"data": snipedata[str(ctx.guild.id)]}})
                await ctx.respond(f"Removed role {role.mention} from whitelist", allowed_mentions=discord.AllowedMentions.none())
                return
            snipedata[str(ctx.guild.id)]["roles"].append(role.id)
            snipedb.update_one({"_id": str(ctx.guild.id)}, {"$set": {"data": snipedata[str(ctx.guild.id)]}})
            await ctx.respond(f"Whitelisted role {role.mention}", allowed_mentions=discord.AllowedMentions.none())
            return
        if user is not None:
            if user.id in snipedata[str(ctx.guild.id)]["users"]:
                snipedata[str(ctx.guild.id)]["users"].remove(user.id)
                snipedb.update_one({"_id": str(ctx.guild.id)}, {"$set": {"data": snipedata[str(ctx.guild.id)]}})
                await ctx.respond(f"Removed user {user.mention} from whitelist", allowed_mentions=discord.AllowedMentions.none())
                return
            snipedata[str(ctx.guild.id)]["users"].append(user.id)
            snipedb.update_one({"_id": str(ctx.guild.id)}, {"$set": {"data": snipedata[str(ctx.guild.id)]}})
            await ctx.respond(f"Whitelisted user {user.mention}", allowed_mentions=discord.AllowedMentions.none())
            return

    @commands.command(aliases=["s"])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.check(snipe_check), commands.is_owner())
    async def snipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in deletemsg:
            author = deletemsg[channel_id]["author"]
            authorav = deletemsg[channel_id]["authorav"]
            timee = deletemsg[channel_id]["time"]
            content = deletemsg[channel_id]["content"]
        else:
            try:
                c = await self.bot.fetch_channel(channel_id)
                await ctx.reply("There is no deleted message in this channel", mention_author=False)
                return
            except discord.errors.NotFound:
                await ctx.reply("This channel does not exist", mention_author=False)
                return
            except discord.errors.Forbidden:
                await ctx.reply("I do not have permission to view this channel", mention_author=False)
                return

        embed = discord.Embed(description=f"{content}", colour=1752220)
        embed.timestamp = timee
        embed.set_author(name=f"{author}", icon_url=f"{authorav}")
        embed.set_footer(text=f"Deleted in {channel}")
        view = DeleteView(ctx)

        if content.startswith("https://") and " " not in content:
            if content.endswith((".png", ".jpg", ".jpeg", ".gif")):
                embed.set_image(url=content)
                embed.description = ""

        if "attachment" in deletemsg[channel_id]:
            attachment = deletemsg[channel_id]["attachment"]
            content += f"\n:open_file_folder:[Attachment]({attachment})"

        if "img" in deletemsg[channel_id]:
            img = deletemsg[channel_id]["img"]
            img = discord.File(io.BytesIO(img), deletemsg[channel_id]["filename"])
            embed.set_image(url=f"attachment://{img.filename}")
            await ctx.reply(embed=embed, file=img, view=view, mention_author=False)
            return
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command(aliases=["dms"])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.check(snipe_check), commands.is_owner())
    async def dmsnipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in deletemsg:
            author = deletemsg[channel_id]["author"]
            authorav = deletemsg[channel_id]["authorav"]
            timee = deletemsg[channel_id]["time"]
            content = deletemsg[channel_id]["content"]
        else:
            try:
                c = await self.bot.fetch_channel(channel_id)
                await ctx.reply("There is no deleted message in this channel", mention_author=False)
                return
            except discord.errors.NotFound:
                await ctx.reply("This channel does not exist", mention_author=False)
                return
            except discord.errors.Forbidden:
                await ctx.reply("I do not have permission to view this channel", mention_author=False)
                return

        embed = discord.Embed(description=f"{content}", colour=1752220)
        embed.timestamp = timee
        embed.set_author(name=f"{author}", icon_url=f"{authorav}")
        embed.set_footer(text=f"Deleted in {channel}")

        if content.startswith("https://") and " " not in content:
            if content.endswith((".png", ".jpg", ".jpeg", ".gif")):
                embed.set_image(url=content)
                embed.description = ""

        if "attachment" in deletemsg[channel_id]:
            attachment = deletemsg[channel_id]["attachment"]
            content += f"\n:open_file_folder:[Attachment]({attachment})"

        if "img" in deletemsg[channel_id]:
            img = deletemsg[channel_id]["img"]
            img = discord.File(io.BytesIO(img), deletemsg[channel_id]["filename"])
            embed.set_image(url=f"attachment://{img.filename}")
            await ctx.author.send(embed=embed, file=img)
            return
        await ctx.author.send(embed=embed)
        await ctx.message.add_reaction("👍")

    @commands.slash_command(name="snipe", description="shows deleted message in a channel")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.check(snipe_check), commands.is_owner())
    @discord.option(name="channel", type=discord.TextChannel, required=False, default=None)
    @discord.option(name="ephemeral", type=bool, required=False, default=False)
    async def ssnipe(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, ephemeral):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in deletemsg:
            author = deletemsg[channel_id]["author"]
            authorav = deletemsg[channel_id]["authorav"]
            timee = deletemsg[channel_id]["time"]
            content = deletemsg[channel_id]["content"]
        else:
            try:
                c = await self.bot.fetch_channel(channel_id)
                await ctx.respond("There is no deleted message in this channel", ephemeral=True)
                return
            except discord.NotFound:
                await ctx.respond("This channel does not exist", ephemeral=True)
                return
            except discord.Forbidden:
                await ctx.respond("I do not have permission to view this channel", ephemeral=True)
                return

        embed = discord.Embed(description=f"{content}", colour=1752220)
        embed.timestamp = timee
        embed.set_author(name=f"{author}", icon_url=f"{authorav}")
        embed.set_footer(text=f"Deleted in {channel}")

        if ephemeral:
            view = None
        else:
            view = DeleteView(ctx)

        if content.startswith("https://") and " " not in content:
            if content.endswith((".png", ".jpg", ".jpeg", ".gif")):
                embed.set_image(url=content)
                embed.description = ""

        if "attachment" in deletemsg[channel_id]:
            attachment = deletemsg[channel_id]["attachment"]
            content += f"\n:open_file_folder:[Attachment]({attachment})"

        if "img" in deletemsg[channel_id]:
            img = deletemsg[channel_id]["img"]
            img = discord.File(io.BytesIO(img), deletemsg[channel_id]["filename"])
            embed.set_image(url=f"attachment://{img.filename}")
            await ctx.respond(embed=embed, file=img, view=view, ephemeral=ephemeral)
            return
        await ctx.respond(embed=embed, view=view, ephemeral=ephemeral)

    @commands.Cog.listener()
    async def on_message_edit(self, oldmsg, newmsg):
        author = str(oldmsg.author)
        oldcontent = oldmsg.content
        newcontent = newmsg.content
        channel = str(oldmsg.channel.id)
        authav = oldmsg.author.display_avatar.url
        msgurl = oldmsg.jump_url
        timee = newmsg.edited_at or datetime.utcnow()

        if oldmsg.author.bot:
            return

        # remove if you want to snipe nqn messages
        if oldmsg.author.discriminator == "0000":
            return

        else:
            editmsg[channel] = {
                "author": author,
                "oldcontent": oldcontent,
                "newcontent": newcontent,
                "authorav": authav,
                "msgurl": msgurl,
                "time": timee,
            }

    @commands.command(aliases=["es", "editsnipe"])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.check(snipe_check), commands.is_owner())
    async def esnipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in editmsg:
            author = editmsg[channel_id]["author"]
            oldmsg = editmsg[channel_id]["oldcontent"]
            newmsg = editmsg[channel_id]["newcontent"]
            authav = editmsg[channel_id]["authorav"]
            messageurl = editmsg[channel_id]["msgurl"]
            timee = editmsg[channel_id]["time"]
        else:
            try:
                c = await self.bot.fetch_channel(channel_id)
                await ctx.reply("There is no edited message in this channel", mention_author=False)
                return
            except discord.errors.NotFound:
                await ctx.reply("This channel does not exist", mention_author=False)
                return
            except discord.errors.Forbidden:
                await ctx.reply("I do not have permission to view this channel", mention_author=False)
                return

        embed = discord.Embed(description=f"[Jump to message]({messageurl})", colour=1752220)
        embed.add_field(name="Original Message", value=f"{oldmsg}")
        embed.add_field(name="Edited message", value=f"{newmsg}")
        embed.timestamp = timee
        embed.set_author(name=f"{author}", icon_url=f"{authav}")
        embed.set_footer(text=f"Edited in {channel}")
        view = DeleteView(ctx)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    @commands.command(aliases=["dmes"])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.check(snipe_check), commands.is_owner())
    async def dmesnipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in editmsg:
            author = editmsg[channel_id]["author"]
            oldmsg = editmsg[channel_id]["oldcontent"]
            newmsg = editmsg[channel_id]["newcontent"]
            authav = editmsg[channel_id]["authorav"]
            messageurl = editmsg[channel_id]["msgurl"]
            timee = editmsg[channel_id]["time"]
        else:
            try:
                c = await self.bot.fetch_channel(channel_id)
                await ctx.reply("There is no edited message in this channel", mention_author=False)
                return
            except discord.errors.NotFound:
                await ctx.reply("This channel does not exist", mention_author=False)
                return
            except discord.errors.Forbidden:
                await ctx.reply("I do not have permission to view this channel", mention_author=False)
                return

        embed = discord.Embed(description=f"[Jump to message]({messageurl})", colour=1752220)
        embed.add_field(name="Original Message", value=f"{oldmsg}")
        embed.add_field(name="Edited message", value=f"{newmsg}")
        embed.timestamp = timee
        embed.set_author(name=f"{author}", icon_url=f"{authav}")
        embed.set_footer(text=f"Edited in {channel} ({ctx.guild.name})")
        await ctx.author.send(embed=embed)
        await ctx.message.add_reaction("👍")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == "❌":
            s_m = False
            try:
                msg = deletemsg[str(reaction.message.channel.id)]
                msg["DontSnipe"] = True
                s_m = True
            except KeyError:
                pass
            message = await reaction.message.channel.fetch_message(reaction.message.id)
            try:
                snipemsg = await reaction.message.channel.fetch_message(message.reference.message_id)
                s_user = snipemsg.author.id
            except:
                snipemsg = None
                s_user = None

            try:
                s_user = message.interaction_metadata.user.id
            except:
                s_user = None

            if message.author.id == self.bot.user.id:
                if user.id == s_user or user.id in devs:
                    await message.delete()
                    if snipemsg != None:
                        try:
                            await snipemsg.delete()
                        except discord.Forbidden:
                            pass
                        except discord.NotFound:
                            pass
            if s_m == True:
                del msg["DontSnipe"]

    @commands.command(aliases=["d"])
    async def delete(self, ctx):
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id == self.bot.user.id:
            try:
                msg = deletemsg[str(ctx.channel.id)]
                msg["DontSnipe"] = True
            except KeyError:
                pass
            try:
                snipemsg = await ctx.channel.fetch_message(message.reference.message_id)
                s_user = snipemsg.author.id
            except:
                snipemsg = None
                s_user = None

            try:
                s_user = message.interaction_metadata.user.id
            except:
                s_user = None

            if ctx.author.id in devs or ctx.author.id == s_user:
                await message.delete()
                try:
                    await ctx.message.delete()
                    if s_user != None:
                        await snipemsg.delete()
                except discord.Forbidden:
                    pass
                except discord.NotFound:
                    pass
            else:
                try:
                    await ctx.react("<a:nochamp:1021040710142668870>")
                except discord.Forbidden:
                    pass
            try:
                del msg["DontSnipe"]
            except KeyError:
                pass

    @commands.slash_command(name="editsnipe", description="shows the last edited message in a channel")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.check(snipe_check), commands.is_owner())
    @discord.option(name="channel", type=discord.TextChannel, required=False, default=None)
    @discord.option(name="ephemeral", type=bool, required=False, default=False)
    async def editsnipe(self, ctx, channel: discord.TextChannel, ephemeral):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in editmsg:
            author = editmsg[channel_id]["author"]
            oldmsg = editmsg[channel_id]["oldcontent"]
            newmsg = editmsg[channel_id]["newcontent"]
            authav = editmsg[channel_id]["authorav"]
            messageurl = editmsg[channel_id]["msgurl"]
            timee = editmsg[channel_id]["time"]
        else:
            try:
                c = await self.bot.fetch_channel(channel_id)
                await ctx.respond("There is no edited message in this channel", ephemeral=True)
                return
            except discord.errors.NotFound:
                await ctx.respond("This channel does not exist", ephemeral=True)
                return
            except discord.errors.Forbidden:
                await ctx.respond("I do not have permission to view this channel", ephemeral=True)
                return
        if ephemeral:
            view = None
        else:
            view = DeleteView(ctx)

        embed = discord.Embed(description=f"[Jump to message]({messageurl})", colour=1752220)
        embed.add_field(name="Original Message", value=f"{oldmsg}")
        embed.add_field(name="Edited message", value=f"{newmsg}")
        embed.timestamp = timee
        embed.set_author(name=f"{author}", icon_url=f"{authav}")
        embed.set_footer(text=f"Edited in {channel}")
        await ctx.respond(embed=embed, view=view, ephemeral=ephemeral)


def setup(bot):
    bot.add_cog(Snipe(bot))
    print("Snipe cog loaded")
