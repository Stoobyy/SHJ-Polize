import os
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.spotify_menu = app_commands.ContextMenu(name="Spotify", callback=self.spotify_menu_callback)
        self.bot.tree.add_command(self.spotify_menu)


    @app_commands.command(name="spotify", description="get song info from spotify")
    @app_commands.describe(user="user to get song info from")
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


    async def spotify_menu_callback(self, interaction: discord.Interaction, user: discord.Member):
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

    @app_commands.command(name="say", description="say something as the bot")
    @commands.is_owner()
    async def say(self, interaction: discord.Interaction, message: str, guild_id: str, channel_id: str, reply_message_id: str=None):
        try:
            guild: discord.Guild = await self.bot.fetch_guild(int(guild_id))
        except discord.Forbidden:
            await interaction.response.send_message("Guild not found", ephemeral=True)
            return
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
            
        



async def setup(bot):
    await bot.add_cog(Misc(bot))
    print("Misc cog loaded")