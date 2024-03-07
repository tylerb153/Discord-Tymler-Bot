import os
from pydoc import describe
from urllib import response
import discord
from discord import app_commands
from mcrcon import MCRcon #mcrcon is used to create a remote console to your minecraft server
import requests;
import json;

Token_File = open("Token_File.env","r")
TOKEN = Token_File.readline()
Token_File.close()

guild = discord.Object(id=554203267001745419)
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name='whitelist', description='Add your minecraft username to the whitelist')
async def whitelist(interaction: discord.Interaction, username: str):
    print(username)
    finalmsg = username + " has been added" #adds usrname and has been added to the varible finalmsg
    with MCRcon("127.0.0.1", "1234") as mcr: #send the whitelist command to minecraft server
        resp = mcr.command("/whitelist add " + username)
    await interaction.response.send_message(finalmsg)
    await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="Cult 2.0 Members"))

onlineGroup = app_commands.Group(name="online", description='Returns whether the server is up and running or not.')

@onlineGroup.command(name='status', description='Returns whether the server is up and running or not.')
async def status(interaction: discord.Interaction):
    url = "https://api.mcstatus.io/v2/status/java/mc.theminecraftcult.com"
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        print(json_data["online"])
        if (json_data["online"] == True):
            await interaction.response.send_message(":green_circle: The Minecraft Cult Server is online!")
        else:
            tylerUserID = 336959815374864384
            await interaction.response.send_message(f":red_circle: <@{tylerUserID}> The Minecraft Cult Server is Offline! :(")
    else:
        print(f"API call to {url} failed with status code {response.status_code}.")
        await interaction.response.send_message(":warning: Could not check for online status")

roleGroup = app_commands.Group(name='role', description='Manages user roles')

@roleGroup.command(name='add', description='adds a role with the name you select to yourself.')
async def add(interaction: discord.Interaction, name: str):
    customRoleDividerName = "Tylerrrrrr"
    if name == '@everyone':
        await interaction.response.send_message(content=f'You have @everyone by default :man_facepalming:', ephemeral=True)
        return
    
    name = name.strip('@')

    bannedRoles = []
    customRoleFlag = False
    for role in interaction.guild.roles:
        if role.name == customRoleDividerName:
            customRoleFlag = True
        if customRoleFlag:
            bannedRoles.append(role.name) 
    if name in bannedRoles:
            await interaction.response.send_message(content=f"I cannot give you the role **{name}** it is forbidden!", ephemeral=True)
            print(f'Role {name} is forbidden')
            return
     
    for role in interaction.guild.roles:    
        if role.name == name:
            if role in interaction.user.roles:
                await interaction.response.send_message(content=f'You already have the role **{name}**.', ephemeral=True)
                print(f'User has {name} already')
                break
            await interaction.user.add_roles(role)
            await interaction.response.send_message(content=f'Added the role **{name}** to you', ephemeral=True)
            print(f'{name} was added to user')
            break
        if role.name == customRoleDividerName:
            await interaction.user.add_roles(await interaction.guild.create_role(name=name))
            await interaction.response.send_message(content=f'Added the role **{name}** to you', ephemeral=True)
            print(f'Created role {name} and added it to user')
            break

@client.event
async def on_ready():
    print(tree.add_command(onlineGroup))
    print(tree.add_command(roleGroup))
    await tree.sync()
    print("Ready")

client.run(TOKEN)