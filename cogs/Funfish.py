import discord
from discord.ext import commands, tasks
import datetime
from datetime import datetime, timedelta, timezone, time

roles_data = {
    734307600547708978: "{} makes it to <@&734307600547708978>  and has unlocked\n\n**SIKE YOU THOUGHT YOU WOULD GET SOMETHING**",
    734306269430677515: "{} makes it to <@&734306269430677515>  and has unlocked\n\n****BRUH GET A LIFE****",
    734307591630356530: "{} makes it to <@&734307591630356530>  and has unlocked\n\n**Access to <#840867512835899402>**",
    734304865794392094: "{} makes it to <@&734304865794392094>  and has unlocked\n\n**Access to <#778846322207621142>\nAccess to <#808003829554610176>**",
    734302384032841759: "{} makes it to <@&734302384032841759>  and has unlocked\n\n**Access to <#757698806660989044> and <#781917360856629268>\nMedia permission in <#734011317798830111>\nAccess to <#734775619489104025>\nAbility to change nicknames**",
    757698628360863876: "{} makes it to <@&757698628360863876>  and has unlocked\n\n**Access to <#766205292874563585> and <#739215228167782483>**",
    734305511759151144: "{} makes it to <@&734305511759151144>  and has unlocked\n\n**Access to <#734764580663722076>\nGIF permissions in <#734011317798830111>\n<@&734884310192095342> role**",
    734302084350083166: "{} makes it to <@&734302084350083166>  and has unlocked\n\n**Access to <#734892551743471698> \nAccess to Music Voice channels**",
    756979356332589117: "{} makes it to <@&756979356332589117>  and has unlocked\n\n**Ability to send media in <#737189027320430604>\nAbility to obtain <@&737227560534016042> role from <#767320632663998494>**",
}


class Funfish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timestamp = 0
        self.raid = False
        self.funfish_id = 723259592800206940
        self.bump_check.start()
        self.make_visible_task.start()
        self.make_hidden_task.start()

    def dxb_status(self):
        return self.bot.get_guild(self.funfish_id).get_member(763642116953604098).status == discord.Status.online

    @commands.slash_command(name="raiders", description="Ban the raiders", guild_ids=[723259592800206940])
    @commands.bot_has_permissions(ban_members=True)
    @commands.check_any(commands.has_permissions(ban_members=True), commands.is_owner(), commands.has_role(734304865794392094))
    @discord.option(name="raiders", description="Mention the users to ban", required=True)
    async def _raiders(self, ctx, raiders: str):
        allowed_roles = [734056569041322066, 756979356332589117, 734302084350083166]
        users = raiders.split()
        banned_users = []
        for user in users:
            try:
                user_id = int(user.strip("<@!>"))
                target_user = await self.bot.fetch_user(user_id)
                member = ctx.guild.get_member(user_id)
                if member and any(role.id in allowed_roles for role in member.roles):
                    await ctx.guild.ban(target_user, reason="Mass ban via raiders command")
                    banned_users.append(target_user.mention)
            except Exception:
                pass
        embed = discord.Embed(title="Raiders Banned", color=discord.Color.red())
        embed.add_field(name="Banned Users", value="\n".join(banned_users) if banned_users else "None", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.respond(embed=embed)

    @commands.slash_command(name="gulag", description="Banish someone to the gulag", guild_ids=[723259592800206940])
    @commands.bot_has_permissions(manage_roles=True)
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner(), commands.has_role(734304865794392094))
    @discord.option(name="member", description="Mention the user to banish", required=True)
    async def _gulag(self, ctx, member: discord.Member):
        try:
            gulag_role = ctx.guild.get_role(757148530082054194)
            if gulag_role not in member.roles:
                await member.add_roles(gulag_role, reason="Banishment to the gulag by command")
                await ctx.respond(f"{member.mention} has been banished to the gulag")
            else:
                await ctx.respond(f"{member.mention} is already in the gulag.")
        except discord.Forbidden:
            await ctx.respond("I don't have the necessary permissions to banish this user.", ephemeral=True)
        except Exception as e:
            raise e

    @commands.slash_command(name="nikal", description="Kick someone out of the gulag", guild_ids=[723259592800206940])
    @commands.bot_has_permissions(manage_roles=True)
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.is_owner(), commands.has_role(734304865794392094))
    @discord.option(name="member", description="Mention the user to remove from gulag", required=True)
    async def _nikal(self, ctx, member: discord.Member):
        try:
            gulag_role = ctx.guild.get_role(757148530082054194)
            if gulag_role in member.roles:
                await member.remove_roles(gulag_role, reason="Removed from gulag by command")
                await ctx.respond(f"{member.mention} has clutched gulag!")
            else:
                await ctx.respond(f"{member.mention} is not in the gulag.")
        except discord.Forbidden:
            await ctx.respond("I don't have the necessary permissions to modify roles.", ephemeral=True)
        except Exception as e:
            raise e

    @commands.slash_command(name="raid", description="Toggle raid mode", guild_ids=[723259592800206940])
    @commands.check_any(commands.has_permissions(administrator=True), commands.is_owner(), commands.has_role(734304865794392094))
    async def _raid(self, ctx):
        if self.raid:
            self.raid = False
            await ctx.respond("Raid mode has been disabled.")
        else:
            self.raid = True
            await ctx.respond("Raid mode has been enabled.")

    @commands.command(hidden=True)
    async def serverinfo(self, ctx):
        if ctx.guild.id != self.funfish_id:
            return
        embed = discord.Embed(title="FishyMC", description="Version = `1.19 `\nIP = `funfishmc.aternos.me`", colour=2123412)
        embedd = discord.Embed(
            title="Rules",
            description="""1. Swearing is allowed, but don't get personal.\n2. Stealing from people isnt allowed. If you want something, work for it.\n3. Pranks are allowed, as long as it isn't griefing. If something gets griefed, it's your responsibility to fix it.\n4. Cheats are strictly not allowed. Any player found to log on with any kind of hack, this includes hacked clients and mods, will face severe punishments.\n5. Spamming in chats or leaking personal information in chats is stictly not allowed.\nPlayers found to break these rules are subject to severe punishments. These punishments include chat mutes, temporary bans, permanant bans, etc. Punishment will depend on the severity of the offense commited.""",
            colour=1243903,
        )
        await ctx.send(content="FishyMC V(Lost track) is finally live.", embed=embed)
        await ctx.send(embed=embedd)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != self.funfish_id:
            return
        if self.dxb_status():
            return
        if self.raid:
            return
        try:
            channel = await self.bot.fetch_channel(734011317798830111)
            await channel.send(f"Hello there,{member.mention}\nGet yourself some roles from <#767320632663998494>\nHave a great time here in the server!")
        except Exception as e:
            raise e

    @commands.Cog.listener("on_message")
    async def role_assign(self, message: discord.Message):
        if not message.guild:
            return
        if message.guild.id != self.funfish_id:
            return
        if message.channel.id != 734468894949114008:
            return
        if message.author.id != 159985870458322944:
            return
        user = message.mentions[0]
        level = int(message.content.split()[-1].strip("!"))
        roles_to_remove = []
        role_to_assign = None
        if level >= 100:
            role_to_assign = 734307600547708978
        elif level >= 70:
            role_to_assign = 734306269430677515
        elif level >= 65:
            role_to_assign = 734307591630356530
        elif level >= 50:
            role_to_assign = 734304865794392094
        elif level >= 35:
            role_to_assign = 734302384032841759
        elif level >= 25:
            role_to_assign = 757698628360863876
        elif level >= 10:
            role_to_assign = 734305511759151144
            roles_to_remove = [734302084350083166, 756979356332589117, 734056569041322066]
        elif level >= 5:
            role_to_assign = 734302084350083166
            roles_to_remove = [756979356332589117, 734056569041322066]
        elif level >= 3:
            role_to_assign = 756979356332589117
            roles_to_remove = [734056569041322066]
        try:
            guild = message.guild
            role_to_assign_obj = guild.get_role(role_to_assign)
            roles_to_remove_objs = [guild.get_role(role_id) for role_id in roles_to_remove]
            roles_to_remove_objs = [role for role in roles_to_remove_objs if role is not None]
            if role_to_assign_obj and role_to_assign_obj not in user.roles:
                for role in roles_to_remove_objs:
                    if role in user.roles:
                        await user.remove_roles(role)
                await user.add_roles(role_to_assign_obj)
                channel = await guild.fetch_channel(734011317798830111)
                text = roles_data[role_to_assign].format(user.mention)
                await channel.send(embed=discord.Embed(description=text))
        except Exception as e:
            raise e

    @commands.Cog.listener("on_message")
    async def bump_message(self, message):
        if not message.guild:
            return
        if message.guild.id != self.funfish_id:
            return
        if message.author.id != 302050872383242240:
            return
        if message.embeds:
            if message.embeds[0].description.startswith("Bump done"):
                self.timestamp = message.created_at.timestamp()
        
    @commands.Cog.listener("on_message")
    async def bday_react(self, message):
        if not message.guild:
            return
        if message.guild.id != self.funfish_id:
            return
        if message.channel.id != 770003642622410772:
            return
        if message.author.id != 656621136808902656:
            return
        try:
            await message.add_reaction("🎂")
        except Exception as e:
            raise e

    @tasks.loop(seconds=60)
    async def bump_check(self):
        if self.timestamp == 0:
            return
        if self.dxb_status():
            return
        if datetime.now().timestamp() - self.timestamp > 7200:
            try:
                channel: discord.TextChannel = await self.bot.fetch_channel(757581111512530954)
                await channel.send("<@&773548077024804874> the server needs your help. Bump it please")
                self.timestamp = 0
            except Exception as e:
                raise e

    @tasks.loop(time=time(21, 0, tzinfo=timezone.utc))
    async def make_visible_task(self):
        try:
            channel = self.bot.get_channel(774334799510110268)
            if channel:
                guild = channel.guild
                overwrite = channel.overwrites_for(guild.default_role)
                overwrite.view_channel = True
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
        except Exception as e:
            if isinstance(e, commands.errors.BotMissingPermissions):
                pass
            else:
                raise e

    @tasks.loop(time=time(2, 0, tzinfo=timezone.utc))
    async def make_hidden_task(self):
        try:
            channel = self.bot.get_channel(774334799510110268)
            if channel:
                guild = channel.guild
                overwrite = channel.overwrites_for(guild.default_role)
                overwrite.view_channel = False
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
        except Exception as e:
            if isinstance(e, commands.errors.BotMissingPermissions):
                pass
            else:
                raise e

    @make_visible_task.before_loop
    @make_hidden_task.before_loop
    @bump_check.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Funfish(bot))
    print("Funfish cog loaded")
