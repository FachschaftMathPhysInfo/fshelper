# -*- coding: utf-8 -*-

import discord
import json
import asyncio
import collections
import queue
from discord.ext import commands

konsenslevel = ["Konsens ohne Vorbehalt", "Konsens mit leichten Bedenken", "Konsens mit Enthaltung", "Konsens mit beiseite stehen", "Schwere Bedenken", "VETO"]

waitqueue = []
# different data format?

bot = commands.Bot(command_prefix="fs!")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True, help="Konsensumfrage")
async def konsens(ctx):
    if ctx.message.author == bot.user:
        return
    message = await ctx.send("Es wird ein Konsens abgefragt! Bitte stimmt ab: \n(Um den Konsens abzubrechen, einfach irgendeine Nachricht in den Chat posten)")
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")
    await message.add_reaction("4️⃣")
    await message.add_reaction("5️⃣")
    await message.add_reaction("❌")
    def check(author):
        def inner_check(message):
            return message.author == author and message.channel == ctx.channel
        return inner_check
    try:
        mode = await bot.wait_for('message', check=check(ctx.author), timeout=60)
        interruptor = mode.author
        await ctx.send(f"{interruptor.mention} hat den Konsens unterbrochen!")
    except asyncio.TimeoutError:
        await message.remove_reaction("1️⃣", bot.user)
        await message.remove_reaction("2️⃣", bot.user)
        await message.remove_reaction("3️⃣", bot.user)
        await message.remove_reaction("4️⃣", bot.user)
        await message.remove_reaction("5️⃣", bot.user)
        await message.remove_reaction("❌", bot.user)
        konsens = message.reactions
        worst_konsens = 0
        for elem in konsens:
            if elem.emoji == "❌":
                worst_konsens = 6
            elif elem.emoji == "5️⃣" and worst_konsens < 5:
                worst_konsens = 5
            elif elem.emoji == "1️⃣" and worst_konsens < 1:
                worst_konsens = 1
            elif elem.emoji == "2️⃣" and worst_konsens < 2:
                worst_konsens = 2
            elif elem.emoji == "3️⃣" and worst_konsens < 3:
                worst_konsens = 3
            elif elem.emoji == "4️⃣" and worst_konsens < 4:
                worst_konsens = 4
        worstresponse = konsenslevel[worst_konsens - 1]
        if worst_konsens < 5:
            await ctx.send("Es wurde ein " + worstresponse + " erreicht.")
        else:
            await ctx.send(worstresponse + ", es wurde kein Konsens erreicht. Zurück zur Besprechung!")


@bot.command(pass_context=True, help="Meldung")
async def m(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    waitqueue.append(ctx.message.author)
    await ctx.message.add_reaction("✅")

@bot.command(pass_context=True, help="Nächste Meldung drannehmen")
async def next(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    try:
        next_user = waitqueue.pop(0)
        message = f"Als nächstes kommt {next_user.mention} dran."
    except IndexError:
        message = "Es gibt keine neuen Meldungen."    
    await ctx.send(message)

# TODO: see the entire queue in an embed(?)

@bot.command(pass_context=True, help="Zeigt alle ausstehenden Meldungen an")
async def meldungen(ctx):
    global waitqueue
    if ctx.message.author == bot.user:
        return
    embed = discord.Embed(title="Meldungen", color=0x00ff00) # description here
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
