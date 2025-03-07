import discord
import requests
import subprocess
import os
import asyncio
from typing import Any, Optional 
from mcrcon import MCRcon
from botSupport.errorHandling import dmTyler
from botSupport.globalVariables import tylerUserID, cultGuildID

async def whitelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    print(username)
    finalmsg = f'{username} was added to the whitelist' #adds username and has been added to the varible finalmsg
    try:
        # raise Exception("Testing wooooo")
        if (await getServerRunning()):
            with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr: #send the whitelist command to minecraft server
                resp = mcr.command("/whitelist add " + username)
                print(resp)
                if 'whitelisted' in resp:
                    finalmsg = f'**{username}** is already whitelisted'
                elif 'not exist' in resp:
                    finalmsg = f'**{username}** does not exist please double check your username or kill Microsoft'
                    await dmTyler(f'Microsoft sucks so **{username}** apparently doesn\'t exist. Please fix or people will YELL at you 😰')
            print(interaction.guild)
            if interaction.guild is not None and interaction.guild.id == cultGuildID:
                await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="Cult 3.0 Members"))
        else:
            raise Exception('The minecraft server may not be running')
        
        await interaction.edit_original_response(content=finalmsg)
    except Exception as e:
        await interaction.edit_original_response(content=f'I couldn\'t add **{username}** :sob: and have notified <@{tylerUserID}>')
        raise Exception(f'An error occured in the whitelist command with error:\n{e}')

        
## Server Group ##

async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    # print(f'After deferment the interaction is {interaction.response.is_done()}')
    try:
        serverStatus = await getServerRunning()
    except Exception as e:
        await interaction.edit_original_response(content=":warning: Could not check for online status")
        raise Exception(f'An error occured in the status command with error:\n{e}')

    if serverStatus[0] == True:
        print(serverStatus[1]['players']['online'])
        await interaction.edit_original_response(content=f":green_circle: The Minecraft Cult Server is online with {serverStatus[1]['players']['online']} players connected!")
    else:
        print("Server offline")
        if not interaction.user.id == tylerUserID:
            await dmTyler(":rotating_light: The Minecraft Cult Server is Offline! WEEE WOOO WEEE WOOO :rotating_light:")
        await interaction.edit_original_response(content=f":red_circle: The Minecraft Cult Server is Offline! :(")

async def getServerRunning() -> tuple[bool, Any]:
    try:
        # raise Exception("Testing wooooo")
        url = "https://api.mcstatus.io/v2/status/java/mc.theminecraftcult.com"
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            print(json_data["online"])
            if (json_data["online"] == True):
                print(json_data['players']['online'])
                return (True, json_data)
            else:
                print("Server offline")
                return (False, json_data)
        else:
            raise Exception(f"API call to {url} failed with status code {response.status_code}.")
    except Exception as e:
        raise Exception(f'getServerRunning() failed with exception:\n{e}')


## ADMIN COMMANDS ##
async def op(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    resp = ""
    try:    
        if ((await getServerRunning())[0]):
            with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr:
                resp = mcr.command(f'/op {username}')
                await interaction.edit_original_response(content=resp)
        else:
            raise Exception('There is a problem with the minecraft server or op command')
    except Exception as e:
        await interaction.edit_original_response(content=f"I couldn't give operator privliges to {username} :sob:")
        raise Exception(f'An error occured in the op command with error:\n{e}')
    

## Deprecated commands ##
class deprecatedCommands:
    async def start(interaction: discord.Interaction):
        await interaction.response.defer()
        # await interaction.edit_original_response(content="There is no active Minecraft server at this time the Minecraft Cult 2.5 server is shut down.")
        # return
        try:
            if await getServerRunning():
                await interaction.edit_original_response(content="The server is already running, use **/server status** to check 😜")
            else:
                ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("MINECRAFT_SERVER_IP_ADDRESS")}', f'nohup bash {os.getenv("SSH_SCRIPT_PATH")}/serverStart.sh > /dev/null 2>&1 &']
                subprocess.run(ssh_command, capture_output=False, text=True)
                await interaction.edit_original_response(content="The server is starting please don't panic and cry!")
        except Exception as e:
            print(f'An error occured in the start command with error:\n{e}')
            await dmTyler(f'An error occured in the start command with error:\n{e}')
            await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't start the server :sob:")

    async def stop(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.id == tylerUserID:
            await interaction.edit_original_response(content="You do not have permission to use this command")
            return
        try:
            if not await getServerRunning():
                await interaction.edit_original_response(content="The server is already stopped")
            else:
                with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr:
                    resp = mcr.command("say the server is stopping in 10 seconds")
                    print(resp)
                    await asyncio.sleep(10)
                    resp = mcr.command("save-all")
                    print(resp)
                    resp = mcr.command("stop")
                    print(resp)
                await interaction.edit_original_response(content="The server has stopped!")
        except Exception as e:
            print(f'An error occured in the stop command with error:\n{e}')
            await dmTyler(f'An error occured in the stop command with error:\n{e}')
            await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't stop the server for you :sob:")

    async def backup(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not interaction.user.id == tylerUserID:
            await interaction.edit_original_response(content="You do not have permission to use this command")
            return
        try:
            if await getServerRunning():
                ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("MINECRAFT_SERVER_IP_ADDRESS")}', f'nohup echo {os.getenv("SSH_PASSWORD")} | sudo -S bash {os.getenv("SSH_SCRIPT_PATH")}/serverSave.sh > /dev/null 2>&1 &']
                subprocess.run(ssh_command, capture_output=False, text=True)
                await interaction.edit_original_response(content="The server is saving!")
            else:
                await interaction.edit_original_response(content="The server not running so it won't be backed up!")
        except Exception as e:
            print(f'An error occured in the backup command with error:\n{e}')
            await dmTyler(f'An error occured in the backup command with error:\n{e}')
            await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't backup the server :sob:")