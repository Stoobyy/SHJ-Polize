import discord
from discord.ext import commands, bridge
import os
import topgg

devs = (499112914578309120, 700195735689494558)

class VoteCheckError(commands.CheckFailure):
    pass

@topgg.endpoint("/dblwebhook", topgg.WebhookType.BOT, auth=os.environ["BOT_AUTH"])
async def on_bot_vote(vote_data: topgg.BotVoteData, client: bridge.Bot = topgg.data(bridge.Bot)):
    user_id = vote_data.user
    try:
        user = await client.fetch_user(vote_data.user)
    except:
        user = None
    if vote_data.type == "test":
        print(f"Received a test vote by: {user} ({user_id})")
        try:
            await user.send("Test vote for SHJ-Polize was successful!")
        except:
            pass
    else:
        print(f"Received a vote by: {user} ({user_id})")
        try:
            await user.send("Thanks for voting me on top.gg!\n Here's a cookie 🍪")
        except:
            pass

manager = topgg.WebhookManager()
manager.endpoint(on_bot_vote)

dblclient =  topgg.DBLClient(token=os.environ["TOPGG_TOKEN"], default_bot_id=969663219570462790)

async def votecheck( ctx):
    if ctx.author.id in devs:
        return True
    data = await dblclient.get_user_vote(ctx.author.id)
    if data:
        return True
    else:
        raise VoteCheckError("You need to vote for SHJ-Polize on top.gg to use this command! You can vote here : https://top.gg/bot/969663219570462790/vote")
