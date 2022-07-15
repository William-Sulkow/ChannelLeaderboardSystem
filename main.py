import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)


bot_id = 997324002164998254


def dump():
    with open('data.json', 'w') as f:
        json.dump(client.data, f)


def form_lb(g_id, sorted_lb, a):
    lb_keys, lb_values = list(sorted_lb.keys()), list(sorted_lb.values())
    top = ""
    for p in range(a):
        mem = lb_keys[p]
        for m in client.get_guild(g_id).members:
            if str(m.id) == str(lb_keys[p]):
                mem = m.display_name
                break
        top = top + f"{p + 1}.    {mem}: {lb_values[p]}\n"

    return top


client.data = {}


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    with open('data.json') as f:
        client.data = json.load(f)


@client.command()
@commands.has_permissions(administrator=True)
async def init(ctx):
    if str(ctx.guild.id) not in client.data:
        client.data[str(ctx.guild.id)] = {}
    if str(ctx.channel.id) not in client.data[str(ctx.guild.id)]:
        client.data[str(ctx.guild.id)][str(ctx.channel.id)] = {"player_leaderboard": {},
                                                               "deck_leaderboard": {}, "logs": {}}
        await ctx.send("**This channel has been added to the database**", delete_after=5)
    else:
        await ctx.send("```ERROR: this channel is already in the database```", delete_after=3)
    dump()


@client.command()
async def addme(ctx):
    if str(ctx.guild.id) in client.data:
        if str(ctx.channel.id) in client.data[str(ctx.guild.id)]:
            if str(ctx.author.id) not in client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"]:
                client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"][str(ctx.author.id)] = 0
                client.data[str(ctx.guild.id)][str(ctx.channel.id)]["logs"][str(ctx.author.id)] = []
                await ctx.send("**Added**", delete_after=5)
            else:
                await ctx.send(f"```ERROR: you are already in the leaderboard```", delete_after=3)
        else:
            await ctx.send(f"```ERROR: channel has not been added```", delete_after=3)
    else:
        await ctx.send(f"```ERROR: guild has not been added```", delete_after=3)

    dump()


@client.command()
async def removeme(ctx):
    if str(ctx.guild.id) in client.data:
        if str(ctx.channel.id) in client.data[str(ctx.guild.id)]:
            if str(ctx.author.id) in client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"]:
                del client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"][str(ctx.author.id)]
                del client.data[str(ctx.guild.id)][str(ctx.channel.id)]["logs"][str(ctx.author.id)]
            else:
                await ctx.send(f"```ERROR: you are not in the leaderboard```", delete_after=3)
        else:
            await ctx.send(f"```ERROR: channel has not been added```", delete_after=3)
    else:
        await ctx.send(f"```ERROR: guild has not been added```", delete_after=3)

    dump()


@client.command()
async def won(ctx, deck1, mem: discord.Member, deck2):
    if str(ctx.guild.id) in client.data:
        if str(ctx.channel.id) in client.data[str(ctx.guild.id)]:
            if str(ctx.author.id) in client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"] and (int(mem.id) == bot_id or str(
                    mem.id) in client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"]):
                c_data = client.data[str(ctx.guild.id)][str(ctx.channel.id)]
                c_data["player_leaderboard"][str(ctx.author.id)] += 1
                if deck1.lower() in c_data["deck_leaderboard"]:
                    c_data["deck_leaderboard"][deck1.lower()] += 1
                else:
                    c_data["deck_leaderboard"][deck1.lower()] = 1
                if deck2.lower() not in c_data["deck_leaderboard"]:
                    c_data["deck_leaderboard"][deck2.lower()] = 0
                if bot_id == mem.id:
                    c_data["logs"][str(ctx.author.id)].append((deck1, "Stranger", deck2))
                else:
                    c_data["logs"][str(ctx.author.id)].append((deck1, mem.display_name, deck2))
                await ctx.send("Leaderboard has been updated!", delete_after=5)
            else:
                await ctx.send(f"```ERROR: a user is not in leaderboard```", delete_after=3)
        else:
            await ctx.send(f"```ERROR: channel has not been added```", delete_after=3)
    else:
        await ctx.send(f"```ERROR: guild has not been added```", delete_after=3)

    dump()


@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, am=2):
    await ctx.channel.purge(limit=int(am))


@client.command()
async def p_leaderboard(ctx, am=5):
    if str(ctx.guild.id) in client.data:
        if str(ctx.channel.id) in client.data[str(ctx.guild.id)]:
            a = am
            if len(client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"]) < am:
                a = len(client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"])

            sorted_lb = {k: v for k, v in
                         sorted(client.data[str(ctx.guild.id)][str(ctx.channel.id)]["player_leaderboard"].items(),
                                key=lambda item: item[1], reverse=True)}

            top = form_lb(ctx.guild.id, sorted_lb, a)

            embed = discord.Embed(title="PLAYER LEADERBOARDS", description=top, colour=discord.Colour.blue())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"```ERROR: channel has not been added```", delete_after=3)
    else:
        await ctx.send(f"```ERROR: guild has not been added```", delete_after=3)


@client.command()
async def d_leaderboard(ctx, am=5):
    if str(ctx.guild.id) in client.data:
        if str(ctx.channel.id) in client.data[str(ctx.guild.id)]:
            a = int(am)
            if len(client.data[str(ctx.guild.id)][str(ctx.channel.id)]["deck_leaderboard"]) < am:
                a = len(client.data[str(ctx.guild.id)][str(ctx.channel.id)]["deck_leaderboard"])

            sorted_lb = {k: v for k, v in
                         sorted(client.data[str(ctx.guild.id)][str(ctx.channel.id)]["deck_leaderboard"].items(),
                                key=lambda item: item[1], reverse=True)}

            print(sorted_lb)
            top = form_lb(ctx.guild.id, sorted_lb, a)

            embed = discord.Embed(title="DECK LEADERBOARDS", description=top, colour=discord.Colour.red())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"```ERROR: channel has not been added```", delete_after=3)
    else:
        await ctx.send(f"```ERROR: guild has not been added```", delete_after=3)


@client.command()
async def recall(ctx):
    if str(ctx.guild.id) in client.data:
        if str(ctx.channel.id) in client.data[str(ctx.guild.id)]:
            if str(ctx.author.id) in client.data[str(ctx.guild.id)][str(ctx.channel.id)]["logs"]:
                await ctx.author.send("**MATCHES: **")
                for m in client.data[str(ctx.guild.id)][str(ctx.channel.id)]["logs"][str(ctx.author.id)]:
                    await ctx.author.send(f"```{ctx.author.display_name} using {m[0]} vs. {m[1]} using {m[2]}```")
            else:
                await ctx.send("```ERROR: user not in leaderboard```")
        else:
            await ctx.send(f"```ERROR: channel has not been added```", delete_after=3)


@client.command()
async def cmd_help(ctx):
    await ctx.send(
        "```All Commands:\n\nPrefix: ! (ex: !cmd_help)\n\n!init: Adds a channel to the database.\n\n!addme: Adds command sender to the channel's leaderboard.\n\n!removeme: Removes command sender from the channel's leaderboard.\n\n!won [command sender's deck] [opponent] [opponent's deck]: Add a win to the database.\n\n!clear [amount (default=5)]: Clears a specified amount of messages.\n\n!p_leaderboard [amount (default=5)]: Displays the player leaderboard of a specified length.\n\n!d_leaderboard [amount (default=5)]: Displays the deck leaderboard of a specified length.\n\n!recall: Sends the log of every win the command sender has had.```")


client.run('OTk3MzI0MDAyMTY0OTk4MjU0.GtHE6K.RvNIoL11eAsrLMlytEOMQ0EQmMdXjJmvphVEZI')
