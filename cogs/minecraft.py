import discord
from discord.ext import commands

from mojang import MojangAPI
from PIL import Image, ImageFilter
from io import BytesIO
import requests


class Minecraft(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
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
            embed = discord.Embed(title=f"{name}'s status", description=":green_circle: Server is online", color=3066993)
            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{name}")
            embed.add_field(name="IP", value=f"{data['ip']}:{data['port']}", inline=True)
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

    @commands.command(hidden=True)
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="FishyMC", description="Version = `1.19 `\nIP = `funfishmc.aternos.me`", colour=2123412)
        embedd = discord.Embed(
            title="Rules",
            description="""1. Swearing is allowed, but don’t get personal.
    2. Stealing from people isnt allowed. If you want something, work for it.
    3. Pranks are allowed, as long as it isn’t griefing. If something gets griefed, it’s your responsibility to fix it.
    4. Cheats are strictly not allowed. Any player found to log on with any kind of hack, this includes hacked clients and mods, will face severe punishments.
    5. Spamming in chats or leaking personal information in chats is stictly not allowed.


    Players found to break these rules are subject to severe punishments. These punishments include chat mutes, temporary bans, permanant bans, etc. Punishment will depend on the severity of the offense commited.""",
            colour=1243903,
        )
        await ctx.send(content="FishyMC V(Lost track) is finally live.", embed=embed)
        await ctx.send(embed=embedd)

    @commands.command()
    async def cape(self, ctx, username):
        uuid = MojangAPI.get_uuid(username)
        name = MojangAPI.get_username(uuid)
        if name is None:
            await ctx.reply("Invalid username", mention_author=False)
            return

        response = requests.get(f"https://api.capes.dev/load/{name}")
        raw = response.json()

        embeds = []
        files = []
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
            embeds.append(embed)
            files.append(mc_cape)

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
            embeds.append(embed)
            files.append(of_cape)

        if len(embeds) == 0:
            await ctx.send(f"{username} has no capes.")
            return
        await ctx.reply(embeds=embeds, files=files, mention_author=False)


def setup(client):
    client.add_cog(Minecraft(client))
    print("Minecraft cog loaded")
