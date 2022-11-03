import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone

deletemsg = {}
editmsg = {}

tzone = timezone(timedelta(hours=4))

devs = (499112914578309120, 700195735689494558)
roles = [752180974590361652, 734302384032841759]


class Snipe(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
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

        if channel in deletemsg:
            if 'DontSnipe' in deletemsg[channel]:
                return

        deletemsg[channel] = {'content': content, 'author': author, 'authorav': message_author_avatar, 'time': timee}

        if message.attachments:
            attachment = message.attachments[0]
            if attachment.url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                img = await attachment.to_file()
                deletemsg[channel]['img'] = img
            else:
                deletemsg[channel]['attachment'] = attachment.url

    @commands.command(aliases=['s'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.is_owner())
    async def snipe(self, ctx,  channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in deletemsg:
            author = deletemsg[channel_id]['author']
            authorav = deletemsg[channel_id]['authorav']
            timee = deletemsg[channel_id]['time']
            content = deletemsg[channel_id]['content']
        else:
            await ctx.reply('There is no deleted message in this channel', mention_author=False)
            return
        if 'attachment' in deletemsg[channel_id]:
            attachment = deletemsg[channel_id]['attachment']
            content += f"\n:open_file_folder:[Attachment]({attachment})"
        embed = discord.Embed(description=f'{content}', colour=1752220)
        embed.timestamp = timee
        embed.set_author(name=f'{author}', icon_url=f'{authorav}')
        embed.set_footer(text=f'Deleted in {channel}')
        if 'img' in deletemsg[channel_id]:
            img = deletemsg[channel_id]['img']
            embed.set_image(url=f'attachment://{img.filename}')
            await ctx.reply(embed=embed, file=img, mention_author=False)
            return
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=['dms'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.is_owner())
    async def dmsnipe(self, ctx,  channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in deletemsg:
            author = deletemsg[channel_id]['author']
            authorav = deletemsg[channel_id]['authorav']
            timee = deletemsg[channel_id]['time']
            content = deletemsg[channel_id]['content']
        else:
            await ctx.reply('There is no deleted message in this channel', mention_author=False)
            return
        if 'attachment' in deletemsg[channel_id]:
            attachment = deletemsg[channel_id]['attachment']
            content += f"\n:open_file_folder:[Attachment]({attachment})"
        embed = discord.Embed(description=f'{content}', colour=1752220)
        embed.timestamp = timee
        embed.set_author(name=f'{author}', icon_url=f'{authorav}')
        embed.set_footer(text=f'Deleted in {channel} ({ctx.guild.name})')
        if 'img' in deletemsg[channel_id]:
            img = deletemsg[channel_id]['img']
            embed.set_image(url=f'attachment://{img.filename}')
            await ctx.author.send(embed=embed, file=img)
            return
        await ctx.author.send(embed=embed)
        await ctx.message.add_reaction('👍')

    @commands.slash_command(name='snipe')
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.is_owner())
    @discord.option(name='channel', type=discord.TextChannel, required=False, default=None)
    @discord.option(name='ephemeral', type=bool, required=False, default=False)
    async def ssnipe(self, ctx, channel: discord.TextChannel, ephemeral):
        if channel is None:
            channel = ctx.channel
        channel_id = str(channel.id)
        if channel_id in deletemsg:
            author = deletemsg[channel_id]['author']
            authorav = deletemsg[channel_id]['authorav']
            timee = deletemsg[channel_id]['time']
            content = deletemsg[channel_id]['content']
        else:
            try:
                c = await self.client.fetch_channel(channel_id)
                await ctx.respond('There is no deleted message in this channel', ephemeral=True)
                return
            except discord.errors.NotFound:
                await ctx.respond('This channel does not exist', ephemeral=True)
                return
            except discord.errors.Forbidden:
                await ctx.respond('I do not have permission to view this channel', ephemeral=True)
                return
        if 'attachment' in deletemsg[channel_id]:
            attachment = deletemsg[channel_id]['attachment']
            content += f"\n:open_file_folder:[Attachment]({attachment})"
        embed = discord.Embed(description=f'{content}', colour=1752220)
        embed.timestamp = timee
        embed.set_author(name=f'{author}', icon_url=f'{authorav}')
        embed.set_footer(text=f'Deleted in {channel}')
        if 'img' in deletemsg[channel_id]:
            img = deletemsg[channel_id]['img']
            embed.set_image(url=f'attachment://{img.filename}')
            await ctx.respond(embed=embed, file=img, ephemeral=ephemeral)
            return
        await ctx.respond(embed=embed, ephemeral=ephemeral)

    @commands.Cog.listener()
    async def on_message_edit(self, oldmsg, newmsg):
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

    @commands.command(aliases=['es'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.is_owner())
    async def esnipe(self, ctx, channel: discord.TextChannel = None):
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

    @commands.command(aliases=['dmes'])
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.is_owner())
    async def dmesnipe(self, ctx, channel: discord.TextChannel = None):
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

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == '❌':
            try:
                msg = deletemsg[str(reaction.message.channel.id)]
                msg['DontSnipe'] = True
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
                s_user = message.interaction.user.id
            except:
                s_user = None

            if message.author.id == self.client.user.id:
                if user.id == s_user or user.id in devs:
                    await message.delete()
                    if snipemsg != None:
                        await snipemsg.delete()
            try:
                del msg['DontSnipe']
            except KeyError:
                pass

    @commands.command(aliases=['d'])
    async def delete(self, ctx):
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if message.author.id == self.client.user.id:
            try:
                msg = deletemsg[str(ctx.channel.id)]
                msg['DontSnipe'] = True
            except KeyError:
                pass
            try:
                snipemsg = await ctx.channel.fetch_message(message.reference.message_id)
                s_user = snipemsg.author.id
            except:
                snipemsg = None
                s_user = None

            try:
                s_user = message.interaction.user.id
            except:
                s_user = None
                
            if ctx.author.id in devs or ctx.author.id == s_user:
                await message.delete()
                await ctx.message.delete()
                if s_user != None:
                    await snipemsg.delete()
            else:
                await ctx.react('<a:nochamp:972351244700090408>')
            try:
                del msg['DontSnipe']
            except KeyError:
                pass

    @commands.slash_command()
    @commands.check_any(commands.has_permissions(manage_messages=True), commands.has_any_role(*roles), commands.is_owner())
    @discord.option(name='channel', type=discord.TextChannel, required=False, default=None)
    @discord.option(name='ephemeral', type=bool, required=False, default=False)
    async def editsnipe(self, ctx, channel: discord.TextChannel, ephemeral):
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
            await ctx.respond('There is no edited message in this channel', ephemeral=True)
            return
        embed = discord.Embed(description=f'[Jump to message]({messageurl})', colour=1752220)
        embed.add_field(name='Original Message', value=f'{oldmsg}')
        embed.add_field(name='Edited message', value=f'{newmsg}')
        embed.timestamp = timee
        embed.set_author(name=f'{author}', icon_url=f'{authav}')
        embed.set_footer(text=f'Deleted in {channel}')
        await ctx.respond(embed=embed, ephemeral=ephemeral)


def setup(client):
    client.add_cog(Snipe(client))
    print('Snipe cog loaded')
