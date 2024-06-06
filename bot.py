import asyncio
import time
import discord
from discord import app_commands
from discord import FFmpegPCMAudio
from mcrcon import MCRcon #mcrcon is used to create a remote console to your minecraft server
import yt_dlp
import requests
import random
import dotenv
import os
import subprocess
import platform

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

guild = discord.Object(id=554203267001745419)
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

## User ID ##
tylerUserID = 336959815374864384 #Used in multiple commands


@tree.command(name='whitelist', description='Add your minecraft username to the whitelist')

async def whitelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    print(username)
    finalmsg = f'{username} was added to the whitelist' #adds usrname and has been added to the varible finalmsg
 
    try:    
        if (getServerRunning()):
            with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr: #send the whitelist command to minecraft server
                resp = mcr.command("/whitelist add " + username)
                print(resp)
                if 'whitelisted' in resp:
                    finalmsg = f'{username} is already whitelisted'
            await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="Cult 2.5 Members"))
        else:
            raise Exception('The minecraft server may not be running')
    except Exception as e:
        print(f'An error occured in the whitelist command with error:\n{e}')
        finalmsg = f'<@{tylerUserID}> I couldn\'t add {username} :sob:'

    await interaction.edit_original_response(content=finalmsg)
        


serverGroup = app_commands.Group(name="server", description='Contains commands that affect the minecraft server.')

@serverGroup.command(name='status', description='Returns whether the server is up and running or not.')
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    # print(f'After deferment the interaction is {interaction.response.is_done()}')
    url = "https://api.mcstatus.io/v2/status/java/mc.theminecraftcult.com"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        print(json_data["online"])
        if (json_data["online"] == True):
            print(json_data['players']['online'])
            await interaction.edit_original_response(content=f":green_circle: The Minecraft Cult Server is online with {json_data['players']['online']} players connected!")
        else:
            print("Server offline")
            await interaction.edit_original_response(content=f":red_circle: <@{tylerUserID}> The Minecraft Cult Server is Offline! :(")
    else:
        print(f"API call to {url} failed with status code {response.status_code}.")
        await interaction.edit_original_response(content=":warning: Could not check for online status")

@serverGroup.command(name="start", description="If the minecraft server is down start it.")
async def start(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        if getServerRunning():
            await interaction.edit_original_response(content="The server is already running, use **/server status** to check 😜")
        else:
            ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("SSH_HOSTNAME")}', f'nohup bash {os.getenv("SSH_SCRIPT_PATH")}/serverStart.sh > /dev/null 2>&1 &']
            subprocess.run(ssh_command, capture_output=False, text=True)
            await interaction.edit_original_response(content="The server is starting please don't panic and cry!")
    except Exception as e:
        print(f'An error occured in the start command with error:\n{e}')
        await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't start the server :sob:")

adminGroup = app_commands.Group(name="admin", description="Commands that only the admins can use")
@adminGroup.command(name="stop", description="If the minecraft server is running stop it.")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        if not getServerRunning():
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
            await interaction.edit_original_response(content="The server has stopping!")
    except Exception as e:
        print(f'An error occured in the stop command with error:\n{e}')
        await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't stop the server for you :sob:")



roleGroup = app_commands.Group(name='role', description='Manages user roles')

@roleGroup.command(name='add', description='Assigns a role with chosen name and color. Defaults to random color. Accepts hex or Discord colors.')
async def add(interaction: discord.Interaction, name: str, color: str = ""):
    await interaction.response.defer(ephemeral=True)
    color = getColor(color)
    customRoleDividerName = "Tylerrrrrr"
    nameStripped = name.strip('@&<>')

    if name == '@everyone':
        await interaction.edit_original_response(content=f'You have @everyone by default :man_facepalming:', allowed_mentions=False)
        return
    
    bannedRoles = getBannedRoles(interaction)
    # print(bannedRoles)
    if nameStripped in bannedRoles or name in bannedRoles.values():
            await interaction.edit_original_response(content=f"I cannot give you the role **{name}** it is forbidden!", allowed_mentions=False)
            print(f'Role {name} is forbidden')
            return
    
    for role in interaction.guild.roles:    
        # print(f'The role ID is: {role.id}\n The named role is {nameStripped}')
        if role.name == name or str(role.id) == nameStripped:
            if role in interaction.user.roles:
                await interaction.edit_original_response(content=f'You already have the role <@&{role.id}>.')
                print(f'User has {name} already')
                break
            await interaction.user.add_roles(role)
            await interaction.edit_original_response(content=f'Added the role <@&{role.id}> to you')
            print(f'{name} was added to user')
            break
        if role.name == customRoleDividerName:
            createdRole = await interaction.guild.create_role(name=name, color=color)
            await interaction.user.add_roles(createdRole)
            await interaction.edit_original_response(content=f'Added the role <@&{createdRole.id}> to you')
            print(f'Created role {createdRole.name} and added it to user')
            break

@roleGroup.command(name='remove', description='Removes a custom role from you')
async def remove(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    bannedRoles = getBannedRoles(interaction)
    if role.id in bannedRoles:
        await interaction.edit_original_response(content=f'You are not allowed to remove the role **{role.name}** it was assigned to you by the holy <@{tylerUserID}>')
        print(f'Role {role.name} is forbidden cannot remove')
        return
    if role in interaction.user.roles:
        try:
            await interaction.user.remove_roles(role)
        except:
            await interaction.edit_original_response(content=f'Couldn\'t remove the role **{role.name}** from you (an error occurred try again in a few minutes).')
            print('Role removed failed')
            return
        
        await interaction.edit_original_response(content=f'Removed the role **{role.name}** from you.')
        print(f'Removed {role.name} from {interaction.user.display_name}')

        print(f'Amount of members in {role.name}: {len(role.members)}')
        if len(role.members) == 0:
            print(f'Deleting the role: {role.name}')
            await role.delete(reason="0 members are in the role")
            

    else:
        await interaction.edit_original_response(content=f'You don\'t have the role **{role.name}** so I can\'t remove it from you.')
        print(f'{interaction.user.display_name} does not have {role.name}')

mediaGroup = app_commands.Group(name='media', description='Controls to play music/videos from Youtube')

@mediaGroup.command(name='play', description='Youtube url in sweet sweet add-free potentially pirated music come out or resumes it')
async def play(interaction: discord.Interaction, url: str = ''):
    await interaction.response.defer()
    userVC = interaction.user.voice
    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
        return
    if not discord.opus.is_loaded():
        if platform.system() == 'Windows':
            pass
        else:
            discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.1/lib/libopus.0.dylib')
    botVC: discord.VoiceClient = interaction.guild.voice_client
    if not (botVC and botVC.is_connected()):
        try:
            botVC = await interaction.user.voice.channel.connect()
            print(f'Joined {userVC.channel.name}')
        except Exception as e:
            print(f'Error in connecting to {userVC.channel.name}\n{e}')
            await interaction.edit_original_response(content=f'Failed to connect to {userVC.channel.name}')
            return

    if botVC.is_paused():
        botVC.resume()
        await interaction.edit_original_response(content=f'Resuming audio')
        return

    # https://www.youtube.com/playlist?list=PLZCI3QwWlHdSNssf8Wue0AGQhFRqPUhZj
    if 'playlist' in url:
        await interaction.edit_original_response(content=f'Long playlists will take some time to start please be patient')
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ignoreerrors': True,
                'flat_playlist': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                playlistDict = await loop.run_in_executor(None, extractInfo, ydl, url)
                await interaction.edit_original_response(content=f'Playing {url} in {userVC.channel.jump_url}')
                i = 0
                for video in playlistDict['entries']:
                    i += 1
                    print(i)
                    if video is not None:
                        videoInfo = await loop.run_in_executor(None, extractInfo, ydl, video['url'])
                        url2 = videoInfo['formats'][0]['url']
                        playAudio(botVC, url2)
                        while botVC.is_playing():
                            await asyncio.sleep(10)
        except Exception as e:
            await interaction.edit_original_response(content=f'Could not play playlist {url}')
            print(e)
    
    # https://www.youtube.com/watch?v=YI1-9pD7RCI
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ignoreerrors': True,
            'noplaylist': True
        }
        await interaction.edit_original_response(content=f'Playing {url} in {userVC.channel.jump_url}')
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                videoInfo = await loop.run_in_executor(None, extractInfo, ydl, url)
                url2 = videoInfo['url']
                print(url2)
                playAudio(botVC, url2)
        except Exception as e:
            await interaction.edit_original_response(content=f'Could not play {url}')
            print(e)

@mediaGroup.command(name='leave', description='Force the bot to leave the channel at all costs')
async def leave(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        botVC: discord.VoiceClient = interaction.guild.voice_client
        await botVC.disconnect()
        await interaction.edit_original_response(content=(f'Disconnected myself successfully'))
    except Exception as e:
        await interaction.edit_original_response(content=f'Could not disconnect')
        print(f'Could not disconnect voice client in {interaction.guild.name}: {interaction.guild.id}\n{e}')

@mediaGroup.command(name='stop', description='Stops playing audio')
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    userVC = interaction.user.voice
    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
        return
    try:
        botVC: discord.VoiceClient = interaction.guild.voice_client
        if botVC:
            botVC.stop()
        await interaction.edit_original_response(content=(f'Stopped audio successfully'))
    except Exception as e:
        await interaction.edit_original_response(content=f'Could not stop audio')
        print(f'Could not stop audio in {interaction.guild.name}: {interaction.guild.id}\n{e}')

@mediaGroup.command(name='pause', description='Pauses playing audio')
async def pause(interaction: discord.Interaction):
    await interaction.response.defer()
    userVC = interaction.user.voice
    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
        return
    try:
        botVC: discord.VoiceClient = interaction.guild.voice_client
        if botVC and botVC.is_playing():
            botVC.pause()
        await interaction.edit_original_response(content=(f'Paused audio successfully'))
    except Exception as e:
        await interaction.edit_original_response(content=f'Could not pause audio')
        print(f'Could not pause audio in {interaction.guild.name}: {interaction.guild.id}\n{e}')

#TODO - Skip functionality (will probably require a queue system instead)
        
    
## Helper Functions ##
def getColor(color: str):
    color = color.strip('#')
    match color.capitalize():
        case 'Teal':
            return discord.Color.teal()
        case 'Dark_teal':
            return discord.Color.dark_teal()
        case 'Brand_green':
            return discord.Color.brand_green()
        case 'Green':
            return discord.Color.green()
        case 'Dark_green':
            return discord.Color.dark_green()
        case 'Blue':
            return discord.Color.blue()
        case 'Dark_blue':
            return discord.Color.dark_blue()
        case 'Purple':
            return discord.Color.purple()
        case 'Dark_purple':
            return discord.Color.dark_purple()
        case 'Magenta':
            return discord.Color.magenta()
        case 'Dark_magenta':
            return discord.Color.dark_magenta()
        case 'Gold':
            return discord.Color.gold()
        case 'Dark_gold':
            return discord.Color.dark_gold()
        case 'Orange':
            return discord.Color.orange()
        case 'Dark_orange':
            return discord.Color.dark_orange()
        case 'Brand_red':
            return discord.Color.brand_red()
        case 'Red':
            return discord.Color.red()
        case 'Dark_red':
            return discord.Color.dark_red()
        case 'Lighter_grey':
            return discord.Color.lighter_grey()
        case 'Lighter_gray':
            return discord.Color.lighter_gray()
        case 'Dark_grey':
            return discord.Color.dark_grey()
        case 'Dark_gray':
            return discord.Color.dark_gray()
        case 'Light_grey':
            return discord.Color.light_grey()
        case 'Light_gray':
            return discord.Color.light_gray()
        case 'Darker_grey':
            return discord.Color.darker_grey()
        case 'Darker_gray':
            return discord.Color.darker_gray()
        case 'Og_blurple':
            return discord.Color.og_blurple()
        case 'Blurple':
            return discord.Color.blurple()
        case 'Greyple':
            return discord.Color.greyple()
        case 'Dark_theme':
            return discord.Color.dark_theme()
        case 'Fuchsia':
            return discord.Color.fuchsia()
        case 'Yellow':
            return discord.Color.yellow()
        case 'Dark_embed':
            return discord.Color.dark_embed()
        case 'Light_embed':
            return discord.Color.light_embed()
        case 'Pink':
            return discord.Color.pink()
        case _:
            colorToReturn = ''
            try:
                print(color)
                colorToReturn = discord.Color.from_str(f'#{color}')
                print(colorToReturn)
            except:
                colorToReturn = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            return colorToReturn

def getBannedRoles(interaction: discord.Interaction) -> dict:
    bannedRoles = {}
    customRoleDividerName = 'Tylerrrrrr'
    customRoleFlag = False
    for role in interaction.guild.roles:
        if role.name == customRoleDividerName:
            customRoleFlag = True
        if customRoleFlag:
            bannedRoles[role.id] = role.name
    return bannedRoles

def extractInfo(ydl, url):
    return ydl.extract_info(url, download= False)

def playAudio(botVC: discord.VoiceClient, url):
    botVC.play(FFmpegPCMAudio(source=url))

def getServerRunning() -> bool:
    ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("SSH_HOSTNAME")}', f'bash {os.getenv("SSH_SCRIPT_PATH")}/serverStatus.sh']

    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True)

        output = (result.stdout).strip('\n')
        error = result.stderr
        
        if output == "true" and error == '':
            return True
        elif output == "false" and error == '':
            return False
        else:
            raise Exception(f'getServerRunning() failed with error in ssh command: \n{error}')

    except Exception as e:
        print(f'Exeption occured while running ssh command in getServerRunning()\n{e}')
        raise e




## Detect when user enters vc ## 

## Run Discord Client ##
@client.event
async def on_ready():
    tree.clear_commands(guild=None)
    tree.add_command(whitelist)
    tree.add_command(serverGroup)
    tree.add_command(roleGroup)
    tree.add_command(mediaGroup)
    tree.add_command(adminGroup)
    await tree.sync()
    print("Ready")

client.run(TOKEN)

