import discord
import asyncio
import random
import botSupport.globalVariables

async def changeStatusLoop():
    client = botSupport.globalVariables.client
    while not client.is_closed():
        await asyncio.sleep(random.randint(10, 3600))
        print("Changing status")
        await changeStatus()

async def changeStatus():
    client = botSupport.globalVariables.client
    with open('botSupport/statuses.txt', 'r') as file:
        statuses = file.readlines()
        randomStatus = random.choice(statuses).strip()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="The Minecraft Cult", state=randomStatus))
