import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from discord.commands import SlashCommandGroup
import asyncio
import requests
from mojang import API

from PIL import Image, ImageFilter
from io import BytesIO
import requests

CLIENTS = {"Minecraft": "https://cdn.icon-icons.com/icons2/2699/PNG/512/minecraft_logo_icon_168974.png", "Lunar Client": "https://pbs.twimg.com/profile_images/1608698913476812801/uLTLhANK_400x400.jpg", "Badlion": "https://assets.badlion.net/site/assets/badlion-logo.webp", "Feather": "https://pbs.twimg.com/profile_images/1486362057750421507/Lb5PEFp1_400x400.png", "LabyMod": "https://cdn.discordapp.com/app-assets/576456544942686228/605344043886575617.png", "Essential" : "https://cdn.discordapp.com/app-assets/894984875755597825/1006995398029758514.png", "SkyClient" : "https://cdn.discordapp.com/app-assets/857240025288802356/976838645833158666.png"}


class CapeDropdown(discord.ui.Select):
    def __init__(self, embeds, files):
        self.embeds = embeds
        self.files = files
        options = []
        for i in embeds:
            if embeds[i] is not None:
                options.append(discord.SelectOption(label=i))
        super().__init__(placeholder="Select a cape", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embeds[self.values[0]], file=self.files[self.values[0]], view=None)


class CapeView(discord.ui.View):
    def __init__(self, embeds, files):
        super().__init__(CapeDropdown(embeds, files), timeout=180, disable_on_timeout=True)


class Mc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="skin", description="Get a player's skin")
    async def _skin(self, ctx, username):
        MojangAPI = API()
        uuid = MojangAPI.get_uuid(username)
        name = MojangAPI.get_username(uuid)
        if name == None:
            await ctx.respond(f"<:Mike:882149622561243137> {username} is not a valid username.")
            return
        embed = discord.Embed(title=f"{name}'s skin", description=f"[Click here for skin](https://api.mineatar.io/skin/{uuid})", colour=15105570)
        embed.set_image(url=f"https://visage.surgeplay.com/full/{uuid}.png")
        embed.set_thumbnail(url=f"https://api.mineatar.io/face/{uuid}")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=f"{ctx.author.avatar}")
        await ctx.respond(embed=embed)

    @commands.command()
    async def skin(self, ctx, username):
        MojangAPI = API()
        uuid = MojangAPI.get_uuid(username)
        name = MojangAPI.get_username(uuid)
        if name == None:
            await ctx.reply(f"<:Mike:882149622561243137> {username} is not a valid username.")
            return
        embed = discord.Embed(title=f"{name}'s skin", description=f"[Click here for skin](https://api.mineatar.io/skin/{uuid})", colour=15105570)
        embed.set_image(url=f"https://visage.surgeplay.com/full/{uuid}.png")
        embed.set_thumbnail(url=f"https://api.mineatar.io/face/{uuid}")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=f"{ctx.author.avatar}")
        await ctx.reply(embed=embed)

    @commands.command(alias=["ip"])
    async def server(self, ctx, ip=None):
        if ip is None:
            if ctx.guild.id == 723259592800206940:
                ip = "funfishmc.aternos.me"
            else:
                await ctx.reply("Please specify an IP", mention_author=False)
                return
        data = requests.get(f"https://api.mcsrvstat.us/2/{ip}")
        try:
            data = data.json()
        except:
            if ip.endswith(".aternos.me"):
                embed = discord.Embed(title=f"{ip}'s status", description=":red_circle: Server is offline", color=15158332)
                embed.add_field(name="Server IP", value=ip, inline=False)
                await ctx.reply(embed=embed, mention_author=False)
                return
            else:
                await ctx.reply(f"Something went wrong please try again later\n ||{data.text}||", mention_author=False)
                return

        try:
            name = data["hostname"]
        except KeyError:
            name = data["ip"]
        if data["online"] is False:
            embed = discord.Embed(title=f"{name}'s status", description=":red_circle: Server is offline", color=15158332)
            embed.add_field(name="IP", value=f"{data['ip']}:{data['port']}", inline=True)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(title=f"{name}'s status", description=f":green_circle: Server is online | {data['ip']}:{data['port']}", color=3066993)
            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{name}")
            embed.add_field(name="MOTD", value="\n".join(data["motd"]["clean"]), inline=True)
            embed.add_field(name="Version", value=data["version"], inline=True)
            if "software" in data:
                embed.add_field(name="Server Type", value=data["software"], inline=True)
            embed.add_field(name="Players Online", value=f"{data['players']['online']}/{data['players']['max']}", inline=True)
            if data["players"]["online"] != 0:
                try:
                    players = "\n".join(data["players"]["list"])
                    embed.add_field(name="Players", value=f"`{players}`")
                except:
                    pass
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    async def cape(self, ctx, username):
        MojangAPI = API()
        uuid = MojangAPI.get_uuid(username)
        name = MojangAPI.get_username(uuid)
        if name is None:
            await ctx.reply("Invalid username", mention_author=False)
            return

        response = requests.get(f"https://api.capes.dev/load/{name}")
        raw = response.json()

        embeds = {}
        files = {}
        capes = 0
        minecraft = raw["minecraft"]
        optifine = raw["optifine"]

        if minecraft["exists"] == True:
            capeurl = minecraft["frontImageUrl"]
            response = requests.get(capeurl)
            cape = Image.open(BytesIO(response.content))
            cape = cape.resize((636, 1024))

            with BytesIO() as capeimg:
                cape.save(capeimg, format="png")
                capeimg.seek(0)
                mc_cape = discord.File(capeimg, filename="cape.png")

            embed = discord.Embed(title=f"{name}'s Mojang cape", description=f"[Click here for cape]({capeurl})", colour=15105570)
            embed.set_image(url=f"attachment://cape.png")
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{uuid}?overlay")
            embeds["minecraft"] = embed
            files["minecraft"] = mc_cape
            capes += 1
        else:
            embeds["minecraft"] = None
            files["minecraft"] = None

        if optifine["exists"] == True:
            capeurl = optifine["frontImageUrl"]
            response = requests.get(capeurl)
            cape = Image.open(BytesIO(response.content))
            cape = cape.resize((636, 1024))

            with BytesIO() as capeimg:
                cape.save(capeimg, format="png")
                capeimg.seek(0)
                of_cape = discord.File(capeimg, filename="optifine.png")

            embed = discord.Embed(title=f"{name}'s Optifine cape", description=f"[Click here for cape]({capeurl})", colour=15105570)
            embed.set_image(url=f"attachment://optifine.png")
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{uuid}?overlay")
            embeds["optifine"] = embed
            files["optifine"] = of_cape
            capes += 1
        else:
            embeds["optifine"] = None
            files["optifine"] = None

        if capes == 0:
            await ctx.send(f"{username} has no capes.")
            return
        embed = discord.Embed(
            title=f"{name}'s capes",
            description=f"{'✅' if embeds['optifine'] else '❌'} Optifine\n{'✅' if embeds['minecraft'] else '❌'} Minecraft",
            colour=15105570,
        )
        await ctx.send(embed=embed, view=CapeView(embeds, files))

    @commands.slash_command(name="cape", description="Get a player's cape")
    async def _cape(self, ctx: discord.ApplicationContext, username: str):
        await ctx.defer()
        MojangAPI = API()
        uuid = MojangAPI.get_uuid(username)
        name = MojangAPI.get_username(uuid)
        if name is None:
            await ctx.followup.send("Invalid username", mention_author=False)
            return

        response = requests.get(f"https://api.capes.dev/load/{name}")
        raw = response.json()

        embeds = {}
        files = {}
        capes = 0
        minecraft = raw["minecraft"]
        optifine = raw["optifine"]

        if minecraft["exists"] == True:
            capeurl = minecraft["frontImageUrl"]
            response = requests.get(capeurl)
            cape = Image.open(BytesIO(response.content))
            cape = cape.resize((636, 1024))

            with BytesIO() as capeimg:
                cape.save(capeimg, format="png")
                capeimg.seek(0)
                mc_cape = discord.File(capeimg, filename="cape.png")

            embed = discord.Embed(title=f"{name}'s Mojang cape", description=f"[Click here for cape]({capeurl})", colour=15105570)
            embed.set_image(url=f"attachment://cape.png")
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{uuid}?overlay")
            embeds["minecraft"] = embed
            files["minecraft"] = mc_cape
            capes += 1
        else:
            embeds["minecraft"] = None
            files["minecraft"] = None

        if optifine["exists"] == True:
            capeurl = optifine["frontImageUrl"]
            response = requests.get(capeurl)
            cape = Image.open(BytesIO(response.content))
            cape = cape.resize((636, 1024))

            with BytesIO() as capeimg:
                cape.save(capeimg, format="png")
                capeimg.seek(0)
                of_cape = discord.File(capeimg, filename="optifine.png")

            embed = discord.Embed(title=f"{name}'s Optifine cape", description=f"[Click here for cape]({capeurl})", colour=15105570)
            embed.set_image(url=f"attachment://optifine.png")
            embed.set_thumbnail(url=f"https://crafatar.com/avatars/{uuid}?overlay")
            embeds["optifine"] = embed
            files["optifine"] = of_cape
            capes += 1
        else:
            embeds["optifine"] = None
            files["optifine"] = None

        if capes == 0:
            await ctx.followup.send(f"{username} has no capes.")
            return
        embed = discord.Embed(
            title=f"{name}'s capes",
            description=f"{'✅' if embeds['optifine'] else '❌'} Optifine\n{'✅' if embeds['minecraft'] else '❌'} Minecraft",
            colour=15105570,
        )
        await ctx.followup.send(embed=embed, view=CapeView(embeds, files))
    
    @commands.slash_command(name='mc_client', description='Get a list of all users playing on a certain client')
    @discord.option(name='client', description='The client to search for', required=True, choices=list(CLIENTS))
    async def client(self, interaction: discord.ApplicationContext, client: str):
        guild = interaction.guild
        members = {}
        icon = CLIENTS[client]
        for member in guild.members:
            if not member.activities:
                continue
            for activity in member.activities:
                if not activity.type == discord.ActivityType.playing:
                    continue
                if activity.name.lower().startswith(client.lower()):
                    text = f"{activity.name} {activity.details} {activity.state} {activity.small_image_text} {activity.large_image_text}"
                    version = None
                    for word in text.split():
                        if word.startswith("1.") and word.split(".")[1].isdigit() and int(word.split(".")[1])<=21 and len(word.split(".")) in [2,3]:
                            version = word
                            break
                    time = activity.start
                    members[member] = time, version
                    
        if len(members) == 0:
            embed = discord.Embed(title=f"No users playing on {client}", color=discord.Color.red())
            embed.set_thumbnail(url = icon)
            embed.set_footer(text='Try again later')
            embed.timestamp = datetime.utcnow()
            await interaction.response.send_message(embed=embed)
            return
        embed = discord.Embed(title=f"Users playing {client}", color=discord.Color.random())
        embed.set_footer(text=f"Total users: {len(members)}")
        embed.set_thumbnail(url=icon)
        embed.timestamp = datetime.utcnow()
        for member in members:
            time = members[member][0]
            if time is None:
                time = "Unknown"
            else:
                time = f"<t:{int(time.timestamp())}:R>"
            version = members[member][1]
            if version is None:
                version = ""
            else:
                version = f"Version: {version} - "
            embed.add_field(name=f"{member.name}", value=f"{version}Started: {time}")
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(Mc(bot))
    print("mc cog loaded")
