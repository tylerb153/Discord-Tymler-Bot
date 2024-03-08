import discord
from discord import app_commands
from mcrcon import MCRcon #mcrcon is used to create a remote console to your minecraft server
import requests;
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
    if platform.system() == 'Windows':
        command = 'tasklist'
    else:
        command = 'ps aux'
    output = subprocess.check_output(command, shell=True).decode()
    if (os.getenv('MC_SERVER_PROCESS_NAME') in output):
        with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr: #send the whitelist command to minecraft server
            resp = mcr.command("/whitelist add " + username)
            print(resp)
            if 'whitelisted' in resp:
                finalmsg = f'{username} is already whitelisted'
        await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="Cult 2.0 Members"))
    else:
        print('The minecraft server may not be running')
        finalmsg = f'<@{tylerUserID}> I couldn\'t add {username} :sob:'

    await interaction.edit_original_response(content=finalmsg)
        


onlineGroup = app_commands.Group(name="online", description='Returns whether the server is up and running or not.')

@onlineGroup.command(name='status', description='Returns whether the server is up and running or not.')
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    # print(f'After deferment the interaction is {interaction.response.is_done()}')
    url = "https://api.mcstatus.io/v2/status/java/mc.theminecraftcult.com"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        print(json_data["online"])
        if (json_data["online"] == True):
            await interaction.edit_original_response(content=":green_circle: The Minecraft Cult Server is online!")
        else:
            print("Server offline")
            await interaction.edit_original_response(content=f":red_circle: <@{tylerUserID}> The Minecraft Cult Server is Offline! :(")
    else:
        print(f"API call to {url} failed with status code {response.status_code}.")
        await interaction.edit_original_response(content=":warning: Could not check for online status")

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

## Run Discord Client ##
@client.event
async def on_ready():
    tree.clear_commands(guild=None)
    tree.add_command(whitelist)
    tree.add_command(onlineGroup)
    tree.add_command(roleGroup)
    await tree.sync()
    print("Ready")

client.run(TOKEN)

