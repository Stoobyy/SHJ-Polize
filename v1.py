import os
import asyncio
import json
import random
from datetime import *

import discord
import requests
from discord.commands import slash_command
from discord.ext import commands, tasks
from discord.ui import View

import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://nalin:shjpolize@shj-polize.53wo6.mongodb.net/?retryWrites=true&w=majority")
db = cluster["shj-polize"]
highlightdb = db["hl"]
ezdb = db["ez"]


tzone = timezone(timedelta(hours=4))

giveawaytags = []
mix = {}
editmsg = {}
ignore = []
idict = {}
ez = ["Wait... This isn't what I typed!", 'Anyone else really like Rick Astley?', 'Hey helper, how play game?', 'Sometimes I sing soppy, love songs in the car.', 'I like long walks on the beach.', 'Please go easy on me, this is my first time on discord!', "You're a great person! Do you want to chat?", 'In my free time I like to watch cat videos on Youtube', 'When I saw the witch with the potion, I knew there was trouble brewing.', 'If the Minecraft world is infinite, how is the sun spinning around it?', 'Hello everyone! I am an innocent person who loves chatting.', 'Plz give me doggo memes!', 'I heard you like Minecraft, so I built a computer in Minecraft in your Minecraft so you can Minecraft while you Minecraft', "Why can't the Ender Dragon read a book? Because he always starts at the End.", 'Maybe we can have a rematch?',
      'I sometimes try to say bad things then this happens :(', 'Behold, the great and powerful, my magnificent and almighty nemisis!', 'Doin a bamboozle fren.', 'Your comebacks are godly.', 'What happens if I add chocolate milk to macaroni and cheese?', 'Can you paint with all the colors of the wind', 'Blue is greener than purple for sure', 'I had something to say, then I forgot it.', 'When nothing is right, go left.', 'I need help, teach me how to play!', 'Your personality shines brighter than the sun.', 'You are very good at the game friend.', 'I like pineapple on my pizza', 'I like pasta, do you prefer nachos?', 'I like fighting but you are truly better than me!', 'I have really enjoyed playing with you! <3', 'ILY <3', "Pineapple doesn't go on pizza!", 'Lets be friends instead of fighting okay?']

last = {}

client = commands.Bot(command_prefix=commands.when_mentioned_or('>'), help_command=None, intents=discord.Intents.all())

devs = (499112914578309120, 700195735689494558)
roles = [773245326747500604, 734307591630356530, 734304865794392094, 888692319447023636, 888461103250669608, 861175306127933470, 874272681124589629, 860431948236587059, 960209393339731989]


def is_dev(ctx):
    if ctx.author.id in devs:
        return True
    else:
        return False


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.playing, name='with fishes'))


class GiveawayView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎉", style=discord.ButtonStyle.primary, custom_id="gaw_button")
    async def greyu(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id in giveawaytags:
            giveawaytags.remove(interaction.user.id)
            embed = discord.Embed(description="You have successfully been removed from the giveaway!", color=15158332)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            giveawaytags.append(interaction.user.id)
            embed = discord.Embed(title="Success!", description="You have entered the giveaway!", color=2067276)
            await interaction.response.send_message(embed=embed, ephemeral=True)


@client.command()
async def ping(ctx):
    await ctx.send(f"{round(client.latency * 1000)}ms")


@client.listen('on_message')
async def ez_webhook(message):
    if message.author.bot or message.guild is False:
        return

    guildid = message.guild.id
    b = ezdb.find_one({'_id': guildid})
    if b is None:
        ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
        b = ezdb.find_one({'_id': guildid})

    if b['serverwide_blacklist'] is True:
        return
    if message.channel.id in b['channel_blacklist'] or message.author.id in b['user_blacklist']:
        return

    if bool('ez' in message.content.lower().split()) or bool('ez' == message.content.lower()) or bool('ezz' == message.content.lower()) or bool('ezzz' in message.content.lower()) or bool('e z' == message.content.lower()):
        hooks = await message.channel.webhooks()
        hook = discord.utils.get(hooks, name='ezz')
        if hook is None:
            hook = await message.channel.create_webhook(name='ezz', avatar=None, reason=None)

        data = {"content": random.choice(ez), "username": message.author.name, "avatar_url": message.author.avatar.url}
        hookurl = hook.url + '?wait=true'
        response = requests.post(hookurl, json=data)
        raw = response.json()
        channel = await client.fetch_channel(int(raw['channel_id']))
        messageid = await channel.fetch_message(int(raw['id']))

        if message.channel.id in b['channel_deleteafter']:
            t = b['channel_deleteafter'][message.channel.id]
        else:
            if b['server_deleteafter']:
                t = b['server_deleteafter']
            else:
                t = None
        await message.delete()
        if t != None:
            await asyncio.sleep(t)
            await messageid.delete()


@client.listen('on_message')
async def hl_check(message):
    if message.author.bot or message.guild is False:
        return
    guildid = message.guild.id
    current_time = datetime.now(tzone)
    unix_timestamp = current_time.timestamp()
    if guildid in last:
        last[guildid][str(message.author.id)] = unix_timestamp
    else:
        last[guildid] = {str(message.author.id): unix_timestamp}

    ghl = highlightdb.find_one({'_id': guildid})
    if ghl is None:
        highlightdb.insert_one({'_id': guildid, 'hl': {}})
        guildhl = highlightdb.find_one({'_id': guildid})
    else:
        guildhl = ghl['hl']

    for user in guildhl:
        for msg in guildhl[user]:
            if msg.upper() in message.content.upper().split():
                message1 = []
                async for i in message.channel.history(limit=5):
                    timee = i.created_at
                    message1.append(f'**[{timee.strftime("%H:%M:%S")}] {i.author.name}**: {i.content}\n')
                message1.reverse()
                embed = discord.Embed(title=f'**{msg}**', description=f'{"".join(message1)}\n**Source Message**\n[Jump to message]({message.jump_url})', color=1752220)
                embed.set_footer(text=f'Message ID: {message.id} | Author ID: {message.author.id}')
                member = message.guild.get_member(int(str(user)))
                timee = datetime.now(tzone).timestamp()
                lastt = last[guildid][user] if user in last[guildid] else 0
                if lastt == 0 or timee - lastt > 300:
                    await member.send(f"In **{message.guild.name}** {message.channel.mention}, you were mentioned with highlight word \"{msg}\"", embed=embed)


@client.slash_command(name='hl')
async def hl(ctx, word=None):

    guildid = ctx.guild.id
    ghl = highlightdb.find_one({'_id': guildid})
    if ghl is None:
        highlightdb.insert_one({'_id': guildid, 'hl': {}})
        guildhl = highlightdb.find_one({'_id': guildid})
    else:
        guildhl = ghl['hl']

    if word != None:
        if str(ctx.author.id) in guildhl:
            if word in guildhl[str(ctx.author.id)]:
                guildhl[str(ctx.author.id)].remove(word)
                highlightdb.update_one({'_id': guildid}, {'$set': {'hl': guildhl}})
                await ctx.respond(f'{word} has been removed from your highlight list', ephemeral=True)
            else:
                guildhl[str(ctx.author.id)].append(word)
                highlightdb.update_one({'_id': guildid}, {'$set': {'hl': guildhl}})
                await ctx.respond(f'{word} has been added to your highlight list', ephemeral=True)
        else:
            guildhl[str(ctx.author.id)] = [word]
            highlightdb.update_one({'_id': guildid}, {'$set': {'hl': guildhl}})
            await ctx.respond(f'{word} has been added to your highlight list', ephemeral=True)
    else:
        if str(ctx.author.id) not in guildhl:
            embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun >hl [word] to add some', color=1752220)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if len(guildhl[str(ctx.author.id)]) == 0:
                embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun >hl [word] to add some', color=1752220)
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                str1 = ''
                for i in guildhl[str(ctx.author.id)]:
                    str1 += f'{i}\n'
                embed = discord.Embed(title='You\'re currently tracking the following words', description=str1, color=1752220)
                await ctx.respond(embed=embed, ephemeral=True)


@client.command()
async def hl(ctx, word=None):
    guildid = ctx.guild.id
    ghl = highlightdb.find_one({'_id': guildid})
    if ghl is None:
        highlightdb.insert_one({'_id': guildid, 'hl': {}})
        guildhl = highlightdb.find_one({'_id': guildid})
    else:
        guildhl = ghl['hl']

    if word != None:
        if str(ctx.author.id) in guildhl:
            if word in guildhl[str(ctx.author.id)]:
                guildhl[str(ctx.author.id)].remove(word)
                highlightdb.update_one({'_id': guildid}, {'$set': {'hl': guildhl}})
                await ctx.reply(f'{word} has been removed from your highlight list')
            else:
                guildhl[str(ctx.author.id)].append(word)
                highlightdb.update_one({'_id': guildid}, {'$set': {'hl': guildhl}})
                await ctx.reply(f'{word} has been added to your highlight list')
        else:
            guildhl[str(ctx.author.id)] = [word]
            highlightdb.update_one({'_id': guildid}, {'$set': {'hl': guildhl}})
            await ctx.reply(f'{word} has been added to your highlight list')
    else:
        if str(ctx.author.id) not in guildhl:
            embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun >hl [word] to add some', color=1752220)
            await ctx.reply(embed=embed)
        else:
            if len(guildhl[str(ctx.author.id)]) == 0:
                embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun >hl [word] to add some', color=1752220)
                await ctx.reply(embed=embed)
            else:
                str1 = ''
                for i in guildhl[str(ctx.author.id)]:
                    str1 += f'{i}\n'
                embed = discord.Embed(title='You\'re currently tracking the following words', description=str1, color=1752220)
                await ctx.reply(embed=embed)


@client.slash_command(name='giveaway')
@commands.check_any(commands.has_permissions(administrator=True), commands.has_permissions(manage_guild=True), commands.check(is_dev))
async def giveaway(ctx, time, prize):
    embed = discord.Embed(color=15844367)
    current_time = datetime.now(timezone.utc)
    unix_timestamp = current_time.timestamp()
    unix_timestamp_plus_5_min = unix_timestamp + (int(time) * 60)
    unix_timestamp_plus_5_min = int(unix_timestamp_plus_5_min)
    embed.add_field(name=f"{prize}", value=f'React with 🎉 to enter!\nEnds: <t:{unix_timestamp_plus_5_min}:R>\nHosted by: {ctx.author.mention}', inline=False)
    message = await ctx.send(':tada: **GIVEAWAY** :tada:', embed=embed, view=GiveawayView())
    await ctx.respond(f'Giveaway has been created successfully!', ephemeral=True)
    await asyncio.sleep(int(time) * 60)
    winner = random.choice(giveawaytags)
    winner = await client.fetch_user(winner)
    await ctx.send(f"{winner.mention} won the giveaway for {prize}!")
    embed = discord.Embed(color=15844367)
    embed.add_field(name=f"{prize}", value=f'~~React with 🎉 to enter!\nEnds: <t:{unix_timestamp_plus_5_min}:R>\nHosted by: {ctx.author.mention}\nWinner: {winner.mention}~~', inline=False)
    await message.edit('~~:tada: **GIVEAWAY** :tada:~~', embed=embed, view=None)
    giveawaytags.clear()


@client.event
async def on_message_delete(message):
    if message.author.bot:
        return

    # remove if you want to snipe nqn messages
    if message.author.discriminator == '0000':
        return

    content = message.content
    author = str(message.author)
    message_author_avatar = str(message.author.avatar)
    channel = str(message.channel.id)
    timee = datetime.now(tzone)

    if channel in mix:
        if 'DontSnipe' in mix[channel]:
            return

    mix[channel] = {'content': content, 'author': author, 'authorav': message_author_avatar, 'time': timee}

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            img = await attachment.to_file()
            mix[channel]['img'] = img
        else:
            mix[channel]['attachment'] = attachment.url


@client.command(aliases=['s'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.check(is_dev))
async def snipe(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    channel_id = str(channel.id)
    print(channel, channel_id)
    if channel_id in mix:
        author = mix[channel_id]['author']
        authorav = mix[channel_id]['authorav']
        timee = mix[channel_id]['time']
        content = mix[channel_id]['content']
    else:
        await ctx.reply('There is no deleted message in this channel', mention_author=False)
        return
    if 'attachment' in mix[channel_id]:
        attachment = mix[channel_id]['attachment']
        content += f"\n:open_file_folder:[Attachment]({attachment})"
    embed = discord.Embed(description=f'{content}', colour=1752220)
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authorav}')
    embed.set_footer(text=f'Deleted in {channel}')
    if 'img' in mix[channel_id]:
        img = mix[channel_id]['img']
        embed.set_image(url=f'attachment://{img.filename}')
        await ctx.reply(embed=embed, file=img, mention_author=False)
        return
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['dms'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.check(is_dev))
async def dmsnipe(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    channel_id = str(channel.id)
    if channel_id in mix:
        author = mix[channel_id]['author']
        authorav = mix[channel_id]['authorav']
        timee = mix[channel_id]['time']
        content = mix[channel_id]['content']
    else:
        await ctx.reply('There is no deleted message in this channel', mention_author=False)
        return
    if 'attachment' in mix[channel_id]:
        attachment = mix[channel_id]['attachment']
        content += f"\n:open_file_folder:[Attachment]({attachment})"
    embed = discord.Embed(description=f'{content}', colour=1752220)
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authorav}')
    embed.set_footer(text=f'Deleted in {channel} ({ctx.guild.name})')
    if 'img' in mix[channel_id]:
        img = mix[channel_id]['img']
        embed.set_image(url=f'attachment://{img.filename}')
        await ctx.author.send(embed=embed, file=img)
        return
    await ctx.author.send(embed=embed)
    await ctx.message.add_reaction('👍')


@client.event
async def on_message_edit(oldmsg, newmsg):
    author = oldmsg.author
    oldcontent = oldmsg.content
    newcontent = newmsg.content
    channel = str(oldmsg.channel.id)
    authav = oldmsg.author.avatar
    msgurl = oldmsg.jump_url
    timee = datetime.now(tzone)

    if oldmsg.author.bot:
        return

    # remove if you want to snipe nqn messages
    if oldmsg.author.discriminator == '0000':
        return

    else:
        editmsg[channel] = {'author': author, 'oldcontent': oldcontent, 'newcontent': newcontent, 'authorav': authav, 'msgurl': msgurl, 'time': timee}


@client.command(aliases=['es'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.check(is_dev))
async def esnipe(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    channel_id = str(channel.id)
    if channel_id in editmsg:
        author = editmsg[channel_id]['author']
        oldmsg = editmsg[channel_id]['oldcontent']
        newmsg = editmsg[channel_id]['newcontent']
        authav = editmsg[channel_id]['authorav']
        messageurl = editmsg[channel_id]['msgurl']
        timee = editmsg[channel_id]['time']
    else:
        await ctx.reply('There is no edited message in this channel', mention_author=False)
        return
    embed = discord.Embed(description=f'[Jump to message]({messageurl})', colour=1752220)
    embed.add_field(name='Original Message', value=f'{oldmsg}')
    embed.add_field(name='Edited message', value=f'{newmsg}')
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authav}')
    embed.set_footer(text=f'Deleted in {channel}')
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['dmes'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.check(is_dev))
async def dmesnipe(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    channel_id = str(channel.id)
    if channel_id in editmsg:
        author = editmsg[channel_id]['author']
        oldmsg = editmsg[channel_id]['oldcontent']
        newmsg = editmsg[channel_id]['newcontent']
        authav = editmsg[channel_id]['authorav']
        messageurl = editmsg[channel_id]['msgurl']
        timee = editmsg[channel_id]['time']
    else:
        await ctx.reply('There is no edited message in this channel', mention_author=False)
        return
    embed = discord.Embed(description=f'[Jump to message]({messageurl})', colour=1752220)
    embed.add_field(name='Original Message', value=f'{oldmsg}')
    embed.add_field(name='Edited message', value=f'{newmsg}')
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authav}')
    embed.set_footer(text=f'Edited in {channel} ({ctx.guild.name})')
    await ctx.author.send(embed=embed)
    await ctx.message.add_reaction('👍')


@client.event
async def on_reaction_add(reaction, user):
    m1 = mix[str(reaction.message.channel.id)]
    m1['DontSnipe'] = True
    message = await reaction.message.channel.fetch_message(reaction.message.id)
    try:
        snipemsg = await reaction.message.channel.fetch_message(message.reference.message_id)
        s_user = snipemsg.author.id
    except:
        s_user = None
    if message.author.id == client.user.id:
        if reaction.emoji == '❌':
            if user.id == s_user or user.id in devs:
                await message.delete()
                if s_user != None:
                    await snipemsg.delete()
    del m1['DontSnipe']


@client.command(aliases=['d'])
async def delete(ctx):
    m1 = mix[str(ctx.channel.id)]
    m1['DontSnipe'] = True
    message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    try:
        snipemsg = await ctx.channel.fetch_message(message.reference.message_id)
        s_user = snipemsg.author.id
    except:
        s_user = None
    if message.author.id == client.user.id:
        if ctx.author.id in devs or ctx.author.id == s_user:
            await message.delete()
            await ctx.message.delete()
            if s_user != None:
                await snipemsg.delete()
            del m1['DontSnipe']
    else:
        await ctx.react('<a:nochamp:972351244700090408>')
        del m1['DontSnipe']


@client.command(aliases=['eb'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.check(is_dev))
async def eazyblacklist(ctx, param: discord.Member or discord.TextChannel = None):
    if param is None:
        param = ctx.channel

    guildid = ctx.guild.id
    blacklist = ezdb.find_one({'_id': guildid})
    if blacklist is None:
        ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 5, "channel_deleteafter": {}})
        blacklist = ezdb.find_one({'_id': guildid})

    if isinstance(param, discord.TextChannel):
        if param.id in blacklist['channel_blacklist']:
            blacklist['channel_blacklist'].remove(param.id)
            ezdb.update_one({'_id': guildid}, {'$set': {'channel_blacklist': blacklist['channel_blacklist']}})
            await ctx.message.add_reaction('👍')
            return
        blacklist['channel_blacklist'].append(param.id)
        ezdb.update_one({'_id': guildid}, {'$set': {'channel_blacklist': blacklist['channel_blacklist']}})
        await ctx.message.add_reaction('👍')

    elif isinstance(param, discord.Member):
        if param.id in blacklist['user_blacklist']:
            blacklist['user_blacklist'].remove(param.id)
            ezdb.update_one({'_id': guildid}, {'$set': {'user_blacklist': blacklist['user_blacklist']}})
            await ctx.message.add_reaction('👍')
            return
        blacklist['user_blacklist'].append(param.id)
        ezdb.update_one({'_id': guildid}, {'$set': {'user_blacklist': blacklist['user_blacklist']}})
        await ctx.message.add_reaction('👍')


@client.slash_command(name='ezblacklist')
@commands.check_any(commands.has_permissions(manage_messages=True), commands.check(is_dev))
@discord.option(name='channel', type=discord.TextChannel, default=None, description='The channel to blacklist', required=False)
@discord.option(name='user', type=discord.Member, default=None, description='The user to blacklist', required=False)
@discord.option(name='serverwide', type=bool, default=None, description='Blacklist all channels', required=False)
async def eazyblacklist(ctx, channel: discord.TextChannel, user: discord.Member, serverwide: bool):
    guildid = ctx.guild.id
    b = ezdb.find_one({'_id': guildid})
    if b is None:
        ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
        b = ezdb.find_one({'_id': guildid})
    if channel is None and user is None and serverwide is None:
        embed = discord.Embed(title='Blacklist', description='Shows Blacklisted Channels and Users for ez message', colour=1752220)
        cb = '\n'.join('<#{}>'.format(x) for x in b['channel_blacklist'])
        ub = '\n'.join('<@{}>'.format(x) for x in b['user_blacklist'])
        embed.add_field(name='Serverwide blacklist', value=f"{b['serverwide_blacklist']}")
        if len(b['channel_blacklist']) != 0:
            embed.add_field(name='Channels', value=cb, inline=False)
        if len(b['user_blacklist']) != 0:
            embed.add_field(name='Users', value=ub, inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    if isinstance(channel, discord.TextChannel):
        if channel.id in b['channel_blacklist']:
            b['channel_blacklist'].remove(channel.id)
            ezdb.update_one({'_id': guildid}, {'$set': {'channel_blacklist': b['channel_blacklist']}})
            await ctx.respond(f'<#{channel.id}> is no longer blacklisted', ephemeral=True)
            return
        b['channel_blacklist'].append(channel.id)
        ezdb.update_one({'_id': guildid}, {'$set': {'channel_blacklist': b['channel_blacklist']}})
        await ctx.respond(f'<#{channel.id}> is now blacklisted', ephemeral=True)
        return

    if isinstance(user, discord.Member):
        if user.id in b['user_blacklist']:
            b['user_blacklist'].remove(user.id)
            ezdb.update_one({'_id': guildid}, {'$set': {'user_blacklist': b['user_blacklist']}})
            await ctx.respond(f'<@{user.id}> is no longer blacklisted', ephemeral=True)
            return
        b['user_blacklist'].append(user.id)
        ezdb.update_one({'_id': guildid}, {'$set': {'user_blacklist': b['user_blacklist']}})
        await ctx.respond(f'<@{user.id}> is now blacklisted', ephemeral=True)
        return
    sw = b['serverwide_blacklist']
    if serverwide is True:
        if sw is True:
            await ctx.respond('Serverwide blacklist is already enabled', ephemeral=True)
            return
        b['serverwide_blacklist'] = True
        ezdb.update_one({'_id': guildid}, {'$set': {'serverwide_blacklist': b['serverwide_blacklist']}})
        await ctx.respond(f'Serverwide blacklist is now enabled', ephemeral=True)
    elif serverwide is False:
        if sw is False:
            await ctx.respond('Serverwide blacklist is already disabled', ephemeral=True)
            return
        b['serverwide_blacklist'] = False
        ezdb.update_one({'_id': guildid}, {'$set': {'serverwide_blacklist': b['serverwide_blacklist']}})
        await ctx.respond(f'Serverwide blacklist is now disabled', ephemeral=True)


@client.slash_command(name='ezbtimeout')
@commands.check_any(commands.has_permissions(manage_messages=True), commands.check(is_dev))
@discord.option(name='channel', type=discord.TextChannel, default=None, description='The channel to blacklist if empty changes server timeout', required=False)
@discord.option(name='time', type=int, default=None, description='The time in seconds', required=False)
async def deleteafter(ctx, channel: discord.TextChannel, time: int):
    guildid = ctx.guild.id
    b = ezdb.find_one({'_id': guildid})
    if b is None:
        ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
        b = ezdb.find_one({'_id': guildid})

    if time is None:
        embed = discord.Embed(title='ez Timeout', description='Shows the current timeout')
        if b['server_deleteafter'] == 0:
            embed.add_field(name='Serverwide timeout', value='Disabled', inline=False)
        else:
            embed.add_field(name='Serverwide timeout', value=f"{b['server_deleteafter']} seconds")
        if len(b['channel_deleteafter']) != 0:
            v = ''
            for x, j in b['channel_deleteafter'].items():
                v += f'<#{x}> : {j} seconds\n'
            embed.add_field(name='Channels', value=v, inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if channel is None:
        b['server_deleteafter'] = time
        ezdb.update_one({'_id': guildid}, {'$set': {'server_deleteafter': b['server_deleteafter']}})
        await ctx.respond(f'Server timeout set to {time} seconds', ephemeral=True)
    else:
        if str(channel.id) in b['channel_deleteafter']:
            b['channel_deleteafter'][str(channel.id)] = time
            ezdb.update_one({'_id': guildid}, {'$set': {'channel_deleteafter': b['channel_deleteafter']}})
            await ctx.respond(f'Timeout set to {time} seconds for <#{channel.id}>', ephemeral=True)
        else:
            if b['channel_deleteafter'] == {}:
                b['channel_deleteafter'] = {str(channel.id): time}
            else:
                b['channel_deleteafter'][str(channel.id)] = time
            ezdb.update_one({'_id': guildid}, {'$set': {'channel_deleteafter': b['channel_deleteafter']}})
            await ctx.respond(f'Timeout set to {time} seconds for <#{channel.id}>', ephemeral=True)

@client.command
async def server(ctx, ip):
    if ip is None:
        if ctx.guild.id == '723259592800206940':
            ip = 'funfishmc.aternos.me'
        else:
            await ctx.reply('Please specify an IP')
            return
    data = requests.get(f'https://api.mcsrvstat.us/2/{ip}')
    try:
        data = data.json()
    except:
        await ctx.reply(f'Something went wrong please try again later\n ||{data.text}||')
        return

    try:
        name = data['hostname']
    except KeyError:
        name = data['ip']
    if data['online'] is False:
        embed = discord.Embed(title=f"{name}'s status", description='Server is offline')
        embed.add_field(title='IP', value=f"{data['ip']}:{data['port']}", inline=False)
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title=f"{name}'s status", description='Server is online')
        embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{data['ip']}")
        embed.add_field(title='IP', value=f"{data['ip']}:{data['port']}", inline=False)
        embed.add_field(title='MOTD', value="\n ".join(data['motd']['clean']), inline=False)
        embed.add_field(title='Version', value=data['version'], inline=False)
        embed.add_field(title='Server Type', value=data['software'], inline=False)
        embed.add_field(title='Players Online', value=f"{data['players']['online']}/{data['players']['max']}", inline=False)
        if data['players']['online'] != 0:
            embed.add_field(title='Players', value='\n '.join(data['players']['list']), inline=False)
        await ctx.reply(embed=embed)



@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckAnyFailure or commands.errors.MissingAnyRole or commands.errors.MissingPermissions):
        await ctx.message.add_reaction('<a:nochamp:972351244700090408>')
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.reply('Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(')
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    else:
        await ctx.reply(f'{type(error)}\n{error}')
        raise error


@client.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckAnyFailure or commands.errors.MissingAnyRole or commands.errors.MissingPermissions):
        await ctx.respond('<a:nochamp:972351244700090408>', ephemeral=True)
    elif isinstance(error, commands.errors.ChannelNotFound):
        await ctx.respond('Channel not found\nEither channel is not in guild or bot doesnt have access to that channel :(')
    else:
        await ctx.respond(f'{type(error)}\n{error}', ephemeral=True)
        raise error

try:
    token = os.environ['TOKEN']
except KeyError:
    token = 'OTUyODM0MTMzMzg4ODI4NzMy.Yi7x8A.NJUC1KhacvrodNbMOQncj219lp0'
client.run(token)
