import discord
from mcrcon import MCRcon
import os
import botSupport.globalVariables
from botSupport.commandGroups.server import getServerRunning

async def skitzing(interaction: discord.Interaction, title: str, subtitle: str = ""):
    await interaction.response.defer(ephemeral=True)
    client = botSupport.globalVariables.client
    try:    
        if (await getServerRunning()):
            with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr:
                resp = mcr.command(f'/title @a subtitle "{subtitle}"')
                print(resp)
            with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr: 
                resp = mcr.command(f'/title @a title "{title}"')
                print(resp)
        else:
            raise Exception('jacob call no worky')
        await interaction.delete_original_response()
        
    except Exception as e:
        await interaction.delete_original_response()
        raise Exception(f'An error occured in the skitzing command with error:\n{e}')