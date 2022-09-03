import asyncio
import random
from datetime import *

import discord
import requests
from discord.ext import commands
from discord.commands import SlashCommandGroup
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://nalin:shjpolize@shj-polize.53wo6.mongodb.net/?retryWrites=true&w=majority")
db = cluster["shj-polize"]
ezdb = db["ez"]

ez_list = ["Wait... This isn't what I typed!", 'Anyone else really like Rick Astley?', 'Hey helper, how play game?', 'Sometimes I sing soppy, love songs in the car.', 'I like long walks on the beach.', 'Please go easy on me, this is my first time on discord!', "You're a great person! Do you want to chat?", 'In my free time I like to watch cat videos on Youtube', 'When I saw the witch with the potion, I knew there was trouble brewing.', 'If the Minecraft world is infinite, how is the sun spinning around it?', 'Hello everyone! I am an innocent person who loves chatting.', 'Plz give me doggo memes!', 'I heard you like Minecraft, so I built a computer in Minecraft in your Minecraft so you can Minecraft while you Minecraft', "Why can't the Ender Dragon read a book? Because he always starts at the End.", 'Maybe we can have a rematch?',
      'I sometimes try to say bad things then this happens :(', 'Behold, the great and powerful, my magnificent and almighty nemisis!', 'Doin a bamboozle fren.', 'Your comebacks are godly.', 'What happens if I add chocolate milk to macaroni and cheese?', 'Can you paint with all the colors of the wind', 'Blue is greener than purple for sure', 'I had something to say, then I forgot it.', 'When nothing is right, go left.', 'I need help, teach me how to play!', 'Your personality shines brighter than the sun.', 'You are very good at the game friend.', 'I like pineapple on my pizza', 'I like pasta, do you prefer nachos?', 'I like fighting but you are truly better than me!', 'I have really enjoyed playing with you! <3', 'ILY <3', "Pineapple doesn't go on pizza!", 'Lets be friends instead of fighting okay?']


class Ez(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener('on_message')
    async def ez_webhook(self, message):
        if message.author.bot or message.guild is False:
            return

        guildid = message.guild.id
        blacklist = ezdb.find_one({'_id': guildid})
        if blacklist is None:
            ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
            blacklist = ezdb.find_one({'_id': guildid})

        if blacklist['serverwide_blacklist'] is True:
            return
        if message.channel.id in blacklist['channel_blacklist'] or message.author.id in blacklist['user_blacklist']:
            return

        if "ez" in message.content.lower().replace(" ", ""):
            hooks = await message.channel.webhooks()
            hook = discord.utils.get(hooks, name='ezz')
            if hook is None:
                hook = await message.channel.create_webhook(name='ezz', avatar=None, reason=None)

            data = {"content": random.choice(ez_list), "username": message.author.name, "avatar_url": message.author.avatar.url}
            hookurl = hook.url + '?wait=true'
            response = requests.post(hookurl, json=data)
            raw = response.json()
            channel = await self.client.fetch_channel(int(raw['channel_id']))
            messageid = await channel.fetch_message(int(raw['id']))

            if message.channel.id in blacklist['channel_deleteafter']:
                time = blacklist['channel_deleteafter'][message.channel.id]
            else:
                if blacklist['server_deleteafter']:
                    time = blacklist['server_deleteafter']
                else:
                    time = None
            await message.delete()
            if time != None:
                await asyncio.sleep(time)
                await messageid.delete()

    @commands.command(aliases=['eb'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def blacklist(self, ctx, param: discord.Member or discord.TextChannel = None):
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

    ez = SlashCommandGroup(name="ez", description="ez commands")

    @ez.command(name="blacklist", description="blacklist a channel or user")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    @discord.option(name='channel', type=discord.TextChannel, default=None, description='The channel to blacklist', required=False)
    @discord.option(name='user', type=discord.Member, default=None, description='The user to blacklist', required=False)
    async def eazyblacklist(self, ctx, channel: discord.TextChannel, user: discord.Member):
        guildid = ctx.guild.id
        blacklist = ezdb.find_one({'_id': guildid})
        if blacklist is None:
            ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
            blacklist = ezdb.find_one({'_id': guildid})

        if isinstance(channel, discord.TextChannel):
            if channel.id in blacklist['channel_blacklist']:
                blacklist['channel_blacklist'].remove(channel.id)
                ezdb.update_one({'_id': guildid}, {'$set': {'channel_blacklist': blacklist['channel_blacklist']}})
                await ctx.respond(f'<#{channel.id}> is no longer blacklisted', ephemeral=True)
                return
            blacklist['channel_blacklist'].append(channel.id)
            ezdb.update_one({'_id': guildid}, {'$set': {'channel_blacklist': blacklist['channel_blacklist']}})
            await ctx.respond(f'<#{channel.id}> is now blacklisted', ephemeral=True)
            return

        if isinstance(user, discord.Member):
            if user.id in blacklist['user_blacklist']:
                blacklist['user_blacklist'].remove(user.id)
                ezdb.update_one({'_id': guildid}, {'$set': {'user_blacklist': blacklist['user_blacklist']}})
                await ctx.respond(f'<@{user.id}> is no longer blacklisted', ephemeral=True)
                return
            blacklist['user_blacklist'].append(user.id)
            ezdb.update_one({'_id': guildid}, {'$set': {'user_blacklist': blacklist['user_blacklist']}})
            await ctx.respond(f'<@{user.id}> is now blacklisted', ephemeral=True)
            return
        if channel is None and user is None:
            await ctx.respond(f'You need to specify a channel or user', ephemeral=True)
            return

    @ez.command(name="list", description="list blacklisted channels and users")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    async def eazyblacklistlist(self, ctx):
        guildid = ctx.guild.id
        blacklist = ezdb.find_one({'_id': guildid})
        if blacklist is None:
            ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
            blacklist = ezdb.find_one({'_id': guildid})
            embed = discord.Embed(title='Blacklist', description='Shows Blacklisted Channels and Users for ez message', colour=1752220)
            cb = '\n'.join('<#{}>'.format(x) for x in blacklist['channel_blacklist'])
            ub = '\n'.join('<@{}>'.format(x) for x in blacklist['user_blacklist'])
            embed.add_field(name='Serverwide blacklist', value=f"{blacklist['serverwide_blacklist']}")
            if len(blacklist['channel_blacklist']) != 0:
                embed.add_field(name='Channels', value=cb, inline=False)
            if len(blacklist['user_blacklist']) != 0:
                embed.add_field(name='Users', value=ub, inline=False)
            await ctx.respond(embed=embed, ephemeral=True)

    @ez.command(name="disable", description="disable serverwide blacklist")
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    @discord.option(name="disabled", type=bool, description="Disable serverwide blacklist", required=True)
    async def eazyblacklistdisable(self, ctx, disabled):
        guildid = ctx.guild.id
        blacklist = ezdb.find_one({'_id': guildid})
        if blacklist is None:
            ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
            blacklist = ezdb.find_one({'_id': guildid})
        sw = blacklist['serverwide_blacklist']
        if sw is True:
            if disabled is True:
                await ctx.respond('Serverwide blacklist is already enabled', ephemeral=True)
                return
            else:
                blacklist['serverwide_blacklist'] = False
                ezdb.update_one({'_id': guildid}, {'$set': {'serverwide_blacklist': blacklist['serverwide_blacklist']}})
                await ctx.respond(f'Serverwide blacklist is now disabled', ephemeral=True)
        else:
            if disabled is False:
                await ctx.respond('Serverwide blacklist is already disabled', ephemeral=True)
                return
            else:
                blacklist['serverwide_blacklist'] = True
                ezdb.update_one({'_id': guildid}, {'$set': {'serverwide_blacklist': blacklist['serverwide_blacklist']}})
                await ctx.respond(f'Serverwide blacklist is now enabled', ephemeral=True)
        
    @ez.command(name='timeout', description='Set the timeout for the server')
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.is_owner())
    @discord.option(name='channel', type=discord.TextChannel, default=None, description='The channel to blacklist if empty changes server timeout', required=False)
    @discord.option(name='time', type=int, default=None, description='The time in seconds', required=False)
    async def deleteafter(self, ctx, channel: discord.TextChannel, time: int):
        guildid = ctx.guild.id
        blacklist = ezdb.find_one({'_id': guildid})
        if blacklist is None:
            ezdb.insert_one({'_id': guildid, 'channel_blacklist': [], 'user_blacklist': [], 'serverwide_blacklist': False, "server_deleteafter": 0, "channel_deleteafter": {}})
            blacklist = ezdb.find_one({'_id': guildid})

        if time is None:
            embed = discord.Embed(title='ez Timeout', description='Shows the current timeout')
            if blacklist['server_deleteafter'] == 0:
                embed.add_field(name='Serverwide timeout', value='Disabled', inline=False)
            else:
                embed.add_field(name='Serverwide timeout', value=f"{blacklist['server_deleteafter']} seconds")
            if len(blacklist['channel_deleteafter']) != 0:
                v = ''
                for x, j in blacklist['channel_deleteafter'].items():
                    v += f'<#{x}> : {j} seconds\n'
                embed.add_field(name='Channels', value=v, inline=False)
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if channel is None:
            blacklist['server_deleteafter'] = time
            ezdb.update_one({'_id': guildid}, {'$set': {'server_deleteafter': blacklist['server_deleteafter']}})
            await ctx.respond(f'Server timeout set to {time} seconds', ephemeral=True)
        else:
            if str(channel.id) in blacklist['channel_deleteafter']:
                blacklist['channel_deleteafter'][str(channel.id)] = time
                ezdb.update_one({'_id': guildid}, {'$set': {'channel_deleteafter': blacklist['channel_deleteafter']}})
                await ctx.respond(f'Timeout set to {time} seconds for <#{channel.id}>', ephemeral=True)
            else:
                if blacklist['channel_deleteafter'] == {}:
                    blacklist['channel_deleteafter'] = {str(channel.id): time}
                else:
                    blacklist['channel_deleteafter'][str(channel.id)] = time
                ezdb.update_one({'_id': guildid}, {'$set': {'channel_deleteafter': blacklist['channel_deleteafter']}})
                await ctx.respond(f'Timeout set to {time} seconds for <#{channel.id}>', ephemeral=True)


def setup(client):
    client.add_cog(Ez(client))
    print("Ez cog loaded")
