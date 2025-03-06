import discord
from botSupport.globalVariables import tylerUserID
import botSupport.globalVariables as globalVariables

async def dmTyler(message: str):
    try:
        channel = await globalVariables.client.create_dm(discord.Object(id=tylerUserID))
        await channel.send(content=message)
    except Exception as e:
        print(f'Could not dm Tyler: \n{e}')

def log(message: str):
    with open('log.txt', 'a') as f:
        f.write(f'{message}\n')