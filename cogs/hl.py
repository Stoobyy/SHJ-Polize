import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://nalin:shjpolize@shj-polize.53wo6.mongodb.net/?retryWrites=true&w=majority")
db = cluster["shj-polize"]
highlightdb = db["hl"]

tzone = timezone(timedelta(hours=4))

last = {}

class Highlight(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener('on_message')
    async def hl_check(self, message):
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


    @commands.slash_command(name='hl')
    async def slash_hl(self, ctx, word=None):
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


    @commands.command()
    async def hl(self, ctx, word=None):
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


def setup(client):
    client.add_cog(Highlight(client))
    print('Highlight cog loaded')