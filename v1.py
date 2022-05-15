import asyncio
import json
import random
from datetime import *

import discord
import requests
from discord.commands import slash_command
from discord.ext import commands, tasks
from discord.ui import View

tzone = timezone(timedelta(hours=4))

giveawaytags = []
mix = {}
editmsg = {}
ignore = []
idict = {}
ez = ["Wait... This isn't what I typed!", 'Anyone else really like Rick Astley?', 'Hey helper, how play game?', 'Sometimes I sing soppy, love songs in the car.', 'I like long walks on the beach.', 'Please go easy on me, this is my first time on discord!', "You're a great person! Do you want to chat?", 'In my free time I like to watch cat videos on Youtube', 'When I saw the witch with the potion, I knew there was trouble brewing.', 'If the Minecraft world is infinite, how is the sun spinning around it?', 'Hello everyone! I am an innocent person who loves chatting.', 'Plz give me doggo memes!', 'I heard you like Minecraft, so I built a computer in Minecraft in your Minecraft so you can Minecraft while you Minecraft', "Why can't the Ender Dragon read a book? Because he always starts at the End.", 'Maybe we can have a rematch?', 'I sometimes try to say bad things then this happens :(', 'Behold, the great and powerful, my magnificent and almighty nemisis!', 'Doin a bamboozle fren.', 'Your comebacks are godly.', 'What happens if I add chocolate milk to macaroni and cheese?', 'Can you paint with all the colors of the wind', 'Blue is greener than purple for sure', 'I had something to say, then I forgot it.', 'When nothing is right, go left.', 'I need help, teach me how to play!', 'Your personality shines brighter than the sun.', 'You are very good at the game friend.', 'I like pineapple on my pizza', 'I like pasta, do you prefer nachos?', 'I like fighting but you are truly better than me!', 'I have really enjoyed playing with you! <3', 'ILY <3', "Pineapple doesn't go on pizza!", 'Lets be friends instead of fighting okay?']

with open('bl.json', 'r') as f:
    blacklist = json.load(f)
    if "channel_blacklist" not in blacklist:
        blacklist["channel_blacklist"] = []
    if "user_blacklist" not in blacklist:
        blacklist["user_blacklist"] = []
    with open('bl.json', 'w') as f:
        json.dump(blacklist, f)

client = commands.Bot(command_prefix='>', help_command=None, intents=discord.Intents.all())

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
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@client.listen('on_message')
async def on_message(message):
    with open('last.json', 'r') as f:
        last = json.load(f)
    if message.author.bot or message.guild is False:
        return
    if message.author.id in blacklist['user_blacklist'] or message.channel.id in blacklist['channel_blacklist']:
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
        await message.delete()
        await asyncio.sleep(10)
        await messageid.delete()
        return
    guildid = str(message.guild.id)
    current_time = datetime.now(tzone)
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
                            message1.append(
                                f'**[{timee.strftime("%H:%M:%S")}] {i.author.name}**: {i.content}\n')
                        message1.reverse()
                        embed = discord.Embed(
                            title=f'**{msg}**', description=f'{"".join(message1)}\n**Source Message**\n[Jump to message]({message.jump_url})', color=1752220)
                        embed.set_footer(
                            text=f'Message ID: {message.id} | Author ID: {message.author.id}')
                        member = message.guild.get_member(int(str(user)))
                        timee = datetime.now(tzone).timestamp()
                        lastt = last[guild][user] if user in last[guild] else 0
                        if lastt == 0 or timee - lastt > 300:
                            await member.send(f"In **{message.guild.name}** {message.channel.mention}, you were mentioned with highlight word \"{msg}\"", embed=embed)


@client.slash_command(name='hl')
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
            embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun -hl [word] to add some', color=1752220)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            if len(hl[guildid][str(ctx.author.id)]) == 0:
                embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun -hl [word] to add some', color=1752220)
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                str1 = ''
                for i in hl[guildid][str(ctx.author.id)]:
                    str1 += f'{i}\n'
                embed = discord.Embed(title='You\'re currently tracking the following words', description=str1, color=1752220)
                await ctx.respond(embed=embed, ephemeral=True)

@client.command()
async def hl(ctx, word=None):
    guildid = str(ctx.guild.id)
    with open('hl.json', 'r') as f:
        hl = json.load(f)
    if word != None:
        if guildid not in hl:
            hl[guildid] = {}
            hl[guildid][str(ctx.author.id)] = [word]
            await ctx.reply(f'{word} has been added to your highlight list')
        else:
            if str(ctx.author.id) not in hl[guildid]:
                hl[guildid][str(ctx.author.id)] = [word]
                await ctx.reply(f'{word} has been added to your highlight list')
            else:
                if word in hl[guildid][str(ctx.author.id)]:
                    hl[guildid][str(ctx.author.id)].remove(word)
                    await ctx.reply(f'{word} removed from your highlight list')
                else:
                    hl[guildid][str(ctx.author.id)].append(word)
                    await ctx.reply(f'{word} has been added to your highlight list')
        with open('hl.json', 'w') as f:
            json.dump(hl, f)
    else:
        if guildid not in hl:
            hl[guildid] = {}

        if str(ctx.author.id) not in hl[guildid]:
            embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun -hl [word] to add some', color=1752220)
            await ctx.reply(embed=embed)
        else:
            if len(hl[guildid][str(ctx.author.id)]) == 0:
                embed = discord.Embed(title='Highlight List', description=f'You currently have no highlight words\nRun -hl [word] to add some', color=1752220)
                await ctx.reply(embed=embed)
            else:
                str1 = ''
                for i in hl[guildid][str(ctx.author.id)]:
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
        channel = str(ctx.channel.id)
    else:
        channel = str(channel.id)
    if channel in mix:
        author = mix[channel]['author']
        authorav = mix[channel]['authorav']
        timee = mix[channel]['time']
        content = mix[channel]['content']
    else:
        await ctx.reply('There is no deleted message in this channel', mention_author=False)
        return
    if 'attachment' in mix[channel]:
        attachment = mix[channel]['attachment']
        content += f"\n:open_file_folder:[Attachment]({attachment})"
    embed = discord.Embed(description=f'{content}', colour=1752220)
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authorav}')
    if 'img' in mix[channel]:
        img = mix[channel]['img']
        embed.set_image(url=f'attachment://{img.filename}')
        await ctx.reply(embed=embed, file=img, mention_author=False)
        return
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['dms'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.check(is_dev))
async def dmsnipe(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = str(ctx.channel.id)
    else:
        channel = str(channel.id)
    if channel in mix:
        author = mix[channel]['author']
        authorav = mix[channel]['authorav']
        timee = mix[channel]['time']
        content = mix[channel]['content']
    else:
        await ctx.reply('There is no deleted message in this channel', mention_author=False)
        return
    if 'attachment' in mix[channel]:
        attachment = mix[channel]['attachment']
        content += f"\n:open_file_folder:[Attachment]({attachment})"
    embed = discord.Embed(description=f'{content}', colour=1752220)
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authorav}')
    if 'img' in mix[channel]:
        img = mix[channel]['img']
        embed.set_image(url=img)
    await ctx.author.send(embed=embed)
    await ctx.message.add_reaction('👍')


@client.event
async def on_message_edit(oldmsg, newmsg):
    author = oldmsg.author
    oldcontent = oldmsg.content
    newcontent = newmsg.content
    channel = oldmsg.channel.id
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
        channel = str(ctx.channel.id)
    else:
        channel = str(channel.id)
    if channel in editmsg:
        author = editmsg[channel]['author']
        oldmsg = editmsg[channel]['oldcontent']
        newmsg = editmsg[channel]['newcontent']
        authav = editmsg[channel]['authorav']
        messageurl = editmsg[channel]['msgurl']
        timee = editmsg[channel]['time']
    else:
        await ctx.reply('There is no edited message in this channel', mention_author=False)
        return
    embed = discord.Embed(description=f'[Jump to message]({messageurl})', colour=1752220)
    embed.add_field(name='Original Message', value=f'{oldmsg}')
    embed.add_field(name='Edited message', value=f'{newmsg}')
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authav}')
    await ctx.reply(embed=embed, mention_author=False)


@client.command(aliases=['dmes'])
@commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.check(is_dev))
async def dmesnipe(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = str(ctx.channel.id)
    else:
        channel = str(channel.id)
    if channel in editmsg:
        author = editmsg[channel]['author']
        oldmsg = editmsg[channel]['oldcontent']
        newmsg = editmsg[channel]['newcontent']
        authav = editmsg[channel]['authorav']
        messageurl = editmsg[channel]['msgurl']
        timee = editmsg[channel]['time']
    else:
        await ctx.reply('There is no edited message in this channel', mention_author=False)
        return
    embed = discord.Embed(description=f'[Jump to message]({messageurl})', colour=1752220)
    embed.add_field(name='Original Message', value=f'{oldmsg}')
    embed.add_field(name='Edited message', value=f'{newmsg}')
    embed.timestamp = timee
    embed.set_author(name=f'{author}', icon_url=f'{authav}')
    embed.set_footer(text=f'Edited in {ctx.channel} ({ctx.guild.name})')
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
    
    if isinstance(param, discord.TextChannel):
        if param.id in blacklist['channel_blacklist']:
            blacklist['channel_blacklist'].remove(param.id)
            with open('bl.json', 'w') as f:
                json.dump(blacklist, f)
            await ctx.message.add_reaction('👍')
            return
        blacklist['channel_blacklist'].append(param.id)
        with open('bl.json', 'w') as f:
            json.dump(blacklist, f)
        await ctx.message.add_reaction('👍')

    elif isinstance(param, discord.Member):
        if param.id in blacklist['user_blacklist']:
            blacklist['user_blacklist'].remove(param.id)
            with open('bl.json', 'w') as f:
                json.dump(blacklist, f)
            await ctx.message.add_reaction('👍')
            return
        blacklist['user_blacklist'].append(param.id)
        with open('bl.json', 'w') as f:
            json.dump(blacklist, f)
        await ctx.message.add_reaction('👍')

@client.slash_command(name='blacklist')
@commands.check_any(commands.has_permissions(manage_messages=True), commands.check(is_dev))
@discord.option(name='channel', type=discord.TextChannel, default=None, description='The channel to blacklist', required=False)
@discord.option(name='user', type=discord.Member, default=None, description='The user to blacklist', required=False)
async def eazyblacklist(ctx, channel: discord.TextChannel, user: discord.Member):
    if isinstance(channel, discord.TextChannel):
        if channel.id in blacklist['channel_blacklist']:
            blacklist['channel_blacklist'].remove(channel.id)
            with open('bl.json', 'w') as f:
                json.dump(blacklist, f)
            await ctx.respond(f'<#{channel.id}> is no longer blacklisted', ephemeral=True)
            return
        blacklist['channel_blacklist'].append(channel.id)
        with open('bl.json', 'w') as f:
            json.dump(blacklist, f)
        await ctx.respond(f'<#{channel.id}> is now blacklisted', ephemeral=True)
        return

    if isinstance(user, discord.Member):
        if user.id in blacklist['user_blacklist']:
            blacklist['user_blacklist'].remove(user.id)
            with open('bl.json', 'w') as f:
                json.dump(blacklist, f)
            await ctx.respond(f'<@{user.id}> is no longer blacklisted', ephemeral=True)
            return
        blacklist['user_blacklist'].append(user.id)
        with open('bl.json', 'w') as f:
            json.dump(blacklist, f)
        await ctx.respond(f'<@{user.id}> is now blacklisted', ephemeral=True)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingAnyRole):
        await ctx.message.add_reaction('<a:nochamp:972351244700090408>')

client.run('OTUyODM0MTMzMzg4ODI4NzMy.Yi7x8A.NJUC1KhacvrodNbMOQncj219lp0')
