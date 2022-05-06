import discord
import asyncio
from discord.ext import commands, tasks
from discord.ui import View
import time
import random
from datetime import *
import json
from discord.utils import get

roles = {0: 734056569041322066, 3: 756979356332589117, 5: 734302084350083166, 10: 734305511759151144,
         25: 757698628360863876, 35: 734302384032841759, 50: 734304865794392094, 65: 808060262179012658, 70: 734306269430677515}
startroles = [767016755809091654, 767029516769689601,
              767017209389252658, 767017558095429649, 767017041319428107]
giveawaytags = []


client = discord.Bot(help_command=None, intents=discord.Intents.all())


@client.event
async def on_ready():
    print('Bot is ready!')


class GiveawayView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary, custom_id="gaw_button")
    async def greyu(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id in giveawaytags:
            embed = discord.Embed(
                title="Error!", description="You have already entered the giveaway!", color=15158332)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            giveawaytags.append(interaction.user.id)
            embed = discord.Embed(
                title="Success!", description="You have entered the giveaway!", color=2067276)
            await interaction.response.send_message(embed=embed, ephemeral=True)

@client.listen('on_message')
async def on_message(message):
    with open('last.json', 'r') as f:
        last = json.load(f)
    if message.author.bot or message.guild is False:
        return
    guildid = str(message.guild.id)
    current_time = datetime.now(timezone.utc)
    unix_timestamp = current_time.timestamp()
    if guildid in last:
        last[guildid][str(message.author.id)] = unix_timestamp
    else:
        last[guildid] = {str(message.author.id): unix_timestamp}
    with open('last.json', 'w') as f:
        json.dump(last, f)
    with open('hl.json', 'r') as f:
        hl = json.load(f)
    for guild in hl:
        if guild == str(guildid):
            for user in hl[guild]:
                for msg in hl[guild][user]:
                    if msg.upper() in message.content.upper().split():
                        message1 = []
                        async for i in message.channel.history(limit=5):
                            timee = i.created_at
                            message1.append(f'**[{timee.strftime("%H:%M:%S")}] {i.author.name}**: {i.content}\n')
                        message1.reverse()
                        embed = discord.Embed(
                            title=f'**{msg}**', description=f'{"".join(message1)}\n[Jump to message]({message.jump_url})', color=1752220)
                        embed.set_footer(
                            text=f'Message ID: {message.id} | Author ID: {message.author.id}')
                        member = message.guild.get_member(int(str(user)))
                        timee = datetime.now(timezone.utc).timestamp()
                        lastt = last[guild][user] if user in last[guild] else 0
                        if lastt == 0 or timee - lastt > 300:
                            await member.send(f"In **{message.guild.name}** {message.channel.mention}, you were mentioned with highlight word \"{msg}\"", embed=embed)


@client.command(name='hl')
async def hl(ctx, word=None):
    guildid = str(ctx.guild.id)
    with open('hl.json', 'r') as f:
        hl = json.load(f)
    if word != None:
        if guildid not in hl:
            hl[guildid] = {}
            hl[guildid][str(ctx.author.id)] = [word]
            await ctx.respond(f'{word} has been added to your highlight list', ephemeral=True)
        else:
            if str(ctx.author.id) not in hl[guildid]:
                hl[guildid][str(ctx.author.id)] = [word]
                await ctx.respond(f'{word} has been added to your highlight list', ephemeral=True)
            else:
                if word in hl[guildid][str(ctx.author.id)]:
                    hl[guildid][str(ctx.author.id)].remove(word)
                    await ctx.respond(f'{word} removed from your highlight list', ephemeral=True)
                else:
                    hl[guildid][str(ctx.author.id)].append(word)
                    await ctx.respond(f'{word} has been added to your highlight list', ephemeral=True)
        with open('hl.json', 'w') as f:
            json.dump(hl, f)
    else:
        if guildid not in hl:
            hl[guildid] = {}

        if str(ctx.author.id) not in hl[guildid]:
            embed = discord.Embed(
                title='Highlight List', description=f'You currently have no highlight words\nRun -hl [word] to add some', color=1752220)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if len(hl[guildid][str(ctx.author.id)]) == 0:
                embed = discord.Embed(
                title='Highlight List', description=f'You currently have no highlight words\nRun -hl [word] to add some', color=1752220)
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                str1 = ''
                for i in hl[guildid][str(ctx.author.id)]:
                    str1 += f'{i}\n'
                embed = discord.Embed(
                    title='You\'re currently tracking the following words', description=str1, color=1752220)
                await ctx.respond(embed=embed, ephemeral=True)


@client.command(name='giveaway')
async def giveaway(ctx, time, prize):
    embed = discord.Embed(color=15844367)
    current_time = datetime.now(timezone.utc)
    unix_timestamp = current_time.timestamp()
    unix_timestamp_plus_5_min = unix_timestamp + (int(time) * 60)
    unix_timestamp_plus_5_min = int(unix_timestamp_plus_5_min)
    embed.add_field(
        name=f"{prize}", value=f'React with 🎉 to enter!\nEnds: <t:{unix_timestamp_plus_5_min}:R>\nHosted by: {ctx.author.mention}', inline=False)
    message = await ctx.send(':tada: **GIVEAWAY** :tada:', embed=embed, view=GiveawayView())
    await asyncio.sleep(int(time) * 60)
    winner = random.choice(giveawaytags)
    winner = await client.fetch_user(winner)
    await ctx.send(f"{winner.mention} won the giveaway for {prize}!")
    embed = discord.Embed(color=15844367)
    embed.add_field(
        name=f"{prize}", value=f'~~React with 🎉 to enter!\nEnds: <t:{unix_timestamp_plus_5_min}:R>\nHosted by: {ctx.author.mention}~~', inline=False)
    await message.edit('~~:tada: **GIVEAWAY** :tada:~~', embed=embed, view=None)
    giveawaytags.clear()

client.run('OTUyODM0MTMzMzg4ODI4NzMy.Yi7x8A.NJUC1KhacvrodNbMOQncj219lp0')
