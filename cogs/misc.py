import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import asyncio

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.copy_message = False

    @commands.slash_command()
    async def spotify(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        user = interaction.guild.get_member(user.id)
        if not user.activities:
            await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)
            return
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                embed = discord.Embed(title=activity.title, description=f"by {activity.artist}", color=activity.color, url=activity.track_url)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Album", value=activity.album, inline=False)
                duration = str(datetime.utcnow() - activity.start.replace(tzinfo=None)).split(".")[0].split(":", 1)[1]
                tduration = str(activity.duration).split(".")[0].split(":", 1)[1]
                embed.add_field(name="Duration", value=f"{duration} / {tduration}", inline=False)
                embed.set_author(name=user, icon_url=user.display_avatar.url)
                embed.set_footer(text="Started")
                embed.timestamp = activity.created_at
                await interaction.response.send_message(embed=embed)
                return
        await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)

    @commands.user_command()
    async def spotify(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        user = interaction.guild.get_member(user.id)
        if not user.activities:
            await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)
            return
        for activity in user.activities:
            if isinstance(activity, discord.Spotify):
                embed = discord.Embed(title=activity.title, description=f"by {activity.artist}", color=activity.color, url=activity.track_url)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="Album", value=activity.album, inline=False)
                duration = str(datetime.utcnow() - activity.start.replace(tzinfo=None)).split(".")[0].split(":", 1)[1]
                tduration = str(activity.duration).split(".")[0].split(":", 1)[1]
                embed.add_field(name="Duration", value=f"{duration} / {tduration}", inline=False)
                embed.set_author(name=user, icon_url=user.display_avatar.url)
                embed.set_footer(text="Started")
                embed.timestamp = activity.created_at
                await interaction.response.send_message(embed=embed)
                return
        await interaction.response.send_message("User is not listening to Spotify", ephemeral=True)

    @commands.slash_command(name="say", description="say something as the bot")
    @commands.is_owner()
    async def say(self, interaction: discord.Interaction, message: str, guild_id: str, channel_id: str, reply_message_id: str=None):
        try:
            guild: discord.Guild = await self.bot.fetch_guild(int(guild_id))
        except discord.Forbidden:
            await interaction.response.send_message("Guild not found", ephemeral=True)
            return
        try:
            channel = await guild.fetch_channel(int(channel_id))
        except discord.NotFound:
            await interaction.response.send_message("Channel not found", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
            return
        if reply_message_id:
            try:
                reply_message = await channel.fetch_message(int(reply_message_id))
            except discord.NotFound:
                await interaction.response.send_message("Message not found", ephemeral=True)
                return
            except discord.Forbidden:
                await interaction.response.send_message("Bot does not have permission to reply to messages", ephemeral=True)
                return
            try:
                m = await reply_message.reply(message)
            except discord.Forbidden:
                await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
                return
        else:
            try:
                m = await channel.send(message)
            except discord.Forbidden:
                await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
                return
        await interaction.response.send_message(f"Message sent: {m.jump_url}")

    @commands.slash_command(name="copy", description="you dont wanna know")
    @commands.is_owner()
    async def copy(self, interaction: discord.Interaction, guild_id: str, channel_id: str):
    # copy user messages from one channel to another and timeout after 2 minutes
        try:
            guild: discord.Guild = await self.bot.fetch_guild(int(guild_id))
        except discord.Forbidden:
            await interaction.response.send_message("Error while fetching guild, try again later.", ephemeral=True)
            return
        try:
            channel = await guild.fetch_channel(int(channel_id))
        except discord.NotFound:
            await interaction.response.send_message("Channel not found", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("Bot does not have permission to send messages in that channel", ephemeral=True)
            return
        await interaction.response.send_message("Copy started, timeout in 2 minutes")
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        self.copy_message = True
        while self.copy_message:
            try:
                message = await self.bot.wait_for("message", check=check, timeout=120)
            except asyncio.TimeoutError:
                await interaction.followup.send("Copy timed out", ephemeral=True)
                return
            try:
                if '|' in message.content:
                    content, reply_message_id = message.content.rsplit('|',1)
                    reply_message_id = reply_message_id.strip()
                    if not reply_message_id.isdigit():
                        await channel.send(message.content)
                        continue
                    try:
                        reply_message = await channel.fetch_message(int(reply_message_id))
                    except discord.NotFound:
                        await interaction.followup.send("Message not found", ephemeral=True)
                        return
                    except discord.Forbidden:
                        await interaction.followup.send("Bot does not have permission to reply to messages", ephemeral=True)
                        return
                    if self.copy_message:
                        await channel.send(content, reference=reply_message)
                else:
                    if self.copy_message:
                        await channel.send(message.content)
            except discord.Forbidden:
                await interaction.followup.send("Bot does not have permission to send messages in that channel", ephemeral=True)
                return
        
    @commands.slash_command(name="stop", description="stop the copy command")
    @commands.is_owner()
    async def stop(self, interaction: discord.Interaction):
        if self.copy_message:
            self.copy_message = False
            await interaction.response.send_message("Copy stopped")
        else:
            await interaction.response.send_message("Copy is not running", ephemeral=True)





def setup(bot):
    bot.add_cog(Misc(bot))
    print("Misc cog loaded")