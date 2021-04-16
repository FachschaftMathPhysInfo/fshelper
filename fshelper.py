# -*- coding: utf-8 -*-

import discord
import json
import asyncio
import collections
import queue
from discord.ext import commands

konsenslevels = {
    "1️⃣": {
        "number": 1,
        "long": "Konsens ohne Vorbehalt"
    },
    "2️⃣": {
        "number": 2,
        "long": "Konsens mit leichten Bedenken"
    },
    "3️⃣": {
        "number": 3,
        "long": "Konsens mit Enthaltung"
    },
    "4️⃣": {
        "number": 4,
        "long": "Konsens mit beiseite stehen"
    },
    "5️⃣": {
        "number": 5,
        "long": "Schwere Bedenken"
    },
    "❌": {
        "number": 6,
        "long": "VETO"
    },
}

KONSENS_STANDARD_TIMEOUT = 60

waitqueue = []
# different data format?

bot = commands.Bot(command_prefix="fs!")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(pass_context=True, help="Konsensumfrage <time>")
async def konsens(ctx, timeout=KONSENS_STANDARD_TIMEOUT):
    # delete the invocating message but keep track of the reference
    replied_to = await ctx.fetch_message(ctx.message.reference.message_id
                                         ) if ctx.message.reference else None
    await ctx.message.delete()

    if ctx.message.author == bot.user:
        return
    chosen_timeout = int(timeout)

    message_text = (
        "Es wird ein Konsens abgefragt!\n\n"
        f":alarm_clock: Bitte stimmt in den nächsten {chosen_timeout}s ab!\n\n"
        "*(Um den Konsens abzubrechen, einfach irgendeine Nachricht in den Chat posten)*"
    )
    message = None
    if replied_to:
        message = await replied_to.reply(message_text)
    else:
        message = await ctx.send(message_text)

    for emoji, _ in konsenslevels.items():
        await message.add_reaction(emoji)

    def check(author):
        def inner_check(message):
            return message.author == author and message.channel == ctx.channel

        return inner_check

    try:
        mode = await bot.wait_for('message',
                                  check=check(ctx.author),
                                  timeout=chosen_timeout)
        interruptor = mode.author
        await ctx.send(f"{interruptor.mention} hat den Konsens unterbrochen!")
    except asyncio.TimeoutError:
        await message.edit(
            content=("Der Konsens wurde abgefragt! :rocket:\n\n"
                     ":ballot_box: Festgestelltes Ergebnis:"))
        # remove the initial reactions from the bot
        for emoji, _ in reversed(konsenslevels.items()):
            await message.remove_reaction(emoji, bot.user)

        # update the message
        message = await message.channel.fetch_message(message.id)

        votes = message.reactions
        # filter only defined mappings
        votes = [
            konsenslevels[reaction.emoji] for reaction in votes
            if konsenslevels.get(reaction.emoji)
        ]

        # get the worst one from it
        if votes:
            worst_vote = max(votes, key=lambda x: x["number"])
            if worst_vote["number"] < 5:
                await message.edit(content=message.content +
                                   "\n\n:arrow_right: Es wurde ein " +
                                   worst_vote["long"] + " erreicht.")
            else:
                await ctx.send(
                    ":no_entry_sign: " + worst_vote["long"] +
                    ", es wurde kein Konsens erreicht. Zurück zur Besprechung!"
                )
        else:
            await ctx.send("Es hat niemand abgestimmt!")


@bot.command(pass_context=True, help="Meldung")
async def m(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    waitqueue.append(ctx.message)
    await ctx.message.add_reaction("✅")


@bot.command(pass_context=True, help="Nächste Meldung drannehmen")
async def next(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    try:

        message = waitqueue.pop(0)
        await message.remove_reaction("✅", bot.user)
        await message.add_reaction("☑️")
        message = f"Als nächstes kommt {message.author.mention} dran."
    except IndexError:
        message = "Es gibt keine neuen Meldungen."
    await ctx.send(message)


# TODO: see the entire queue in an embed(?)


@bot.command(pass_context=True, help="Zeigt alle ausstehenden Meldungen an")
async def meldungen(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    embed = discord.Embed(title="Meldungen",
                          color=0x00ff00)  # description here
    message = ""
    i = 1
    for elem in waitqueue:
        message = message + str(i) + ": " + str(elem) + "\n"
        i += 1
    if message == "":
        message = "Es stehen keine Meldungen aus."
    embed.add_field(name="Ausstehende Meldungen:", value=message, inline=False)
    await ctx.send(embed=embed)


@bot.command(pass_context=True, help="Ziehe die jüngste Meldung zurück")
async def zz(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    remove_user = -1
    for i in range(len(waitqueue)):
        if waitqueue[i] == ctx.message.author:
            remove_user = i
    if remove_user != -1:
        waitqueue.pop(i)
    await ctx.message.add_reaction("✅")


with open("config.json") as f:
    config = json.load(f)

api_key = config.get("api_key")
if not api_key:
    raise RuntimeError("Config must contain api_key")

bot.run(api_key)
