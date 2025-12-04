import discord
from discord import app_commands
import dotenv
import os
from typing import Optional
import botSupport.commandGroups.server as server
import botSupport.commandGroups.jacob as jacob
import botSupport.commandGroups.role as roleFunctions
import botSupport.commandGroups.admin as admin
import botSupport.commandGroups.pvp as pvp
import botSupport.commandGroups.pvpAdmin as pvpAdmin
import botSupport.leave as leave
import botSupport.commandGroups.media as media
from botSupport.commandGroups.mention import mention as mentionUser
from botSupport.clientEvents.voiceStateUpdate import playSoundWhenTylerJoinsVC
from botSupport.clientEvents.memberUpdate import forcePVPDeaths
import botSupport.clientEvents.messageSent as messageSent
from botSupport.botSounds import playRandomSoundLoop
from botSupport.botStatus import changeStatusLoop, changeStatus
import botSupport.globalVariables as globalVariables
from botSupport.errorHandling import dmTyler

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

guild = discord.Object(id=554203267001745419)
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

####        Server Commands        ####
@tree.command(name='whitelist', description='Add your minecraft username to the whitelist')
async def whitelist(interaction: discord.Interaction, username: str):
    try:
        await server.whitelist(interaction, username)
    except Exception as e:
        await dmTyler(e)
        
serverGroup = app_commands.Group(name="server", description='Contains commands that affect the minecraft server.')

@serverGroup.command(name='status', description='Returns whether the server is up and running or not.')
async def status(interaction: discord.Interaction):
    try:
        await server.status(interaction)
    except Exception as e:
        await dmTyler(e)

####        Jacob Commands        ####
jacobGroup = app_commands.Group(name="jacob", description="Commands for Jacob")
@jacobGroup.command(name="skitzing", description="Title and subtitle for minecraft server... HUH?!")
async def skitzing(interaction: discord.Interaction, title: str, subtitle: str = ""):
    try:
        await jacob.skitzing(interaction, title, subtitle)
    except Exception as e:
        await dmTyler(e)

####        Admin Commands        ####
adminGroup = app_commands.Group(name="admin", description="Commands that only the admins can use")

@adminGroup.command(name='backup', description='Backs up the minecraft server')
async def backup(interaction: discord.Interaction):
    await interaction.response.send_message(content="This is still a work in progress", ephemeral=True)
    return
    await server.backup(interaction)

@adminGroup.command(name='disconnect', description='Disconnects the bot from the voice channel')
async def disconnect(interaction: discord.Interaction):
    await admin.disconnect(interaction)

@adminGroup.command(name='set_status', description='Sets the status of the bot')
async def set_status(interaction: discord.Interaction, status: str):
    await admin.set_status(interaction, status)

@adminGroup.command(name='play_sound', description='Plays a sound from the SoundEffects folder')
async def play_sound(interaction: discord.Interaction):
    await admin.play_sound(interaction)

@adminGroup.command(name="op", description="Gives user operator privliges")
async def op(interaction: discord.Interaction, username: str):
    try:
        await server.op(interaction, username)
    except Exception as e:
        await dmTyler(e)
    
####        Role Commands        ####
roleGroup = app_commands.Group(name='role', description='Manages user roles')

@roleGroup.command(name='add', description='Assigns a role with chosen name and color. Defaults to random color. Accepts hex or Discord colors.')
async def add(interaction: discord.Interaction, name: str, color: str = ""):
    await roleFunctions.add(interaction, name, color)

@roleGroup.command(name='remove', description='Removes a custom role from you')
async def remove(interaction: discord.Interaction, role: discord.Role):
    await roleFunctions.remove(interaction, role)

####        PVP Commands        ####
pvpGroup = app_commands.Group(name='pvp', description='PVP other discord members')

@pvpGroup.command(name="attack", description="Attack a member and describe how you attacked them.")
async def attack(interaction: discord.Interaction, defender: discord.Member):
    await pvp.attack(interaction, defender)

@pvpGroup.command(name="defend", description="Defend a member's attack and describe how you defended them.")
async def defend(interaction: discord.Interaction):
    await pvp.defend(interaction)

@pvpGroup.command(name='health', description='Check someone\'s health')
async def health(interaction: discord.Interaction, member: discord.Member = None):
    await pvp.health(interaction, member)

@pvpGroup.command(name="battles", description='List all previous battle from person')
async def battles(interaction: discord.Interaction, member: discord.Member = None):
    await pvp.battles(interaction, member)

@pvpGroup.command(name="inventory", description="Show items or use an item")
async def inventory(interaction: discord.Interaction):
    await pvp.inventory(interaction)

@pvpGroup.command(name="stats", description="Show your stats")
async def stats(interaction: discord.Interaction):
    await pvp.stats(interaction)

@pvpGroup.command(name="help", description="Show help for pvp commands")
async def pvp_help(interaction: discord.Interaction):
    await pvp.pvp_help(interaction)

####        PVP Admin Commands        ####
pvpAdminGroup = app_commands.Group(name="pvp_admin", description="Commands that only the pvp admin can use")

@pvpAdminGroup.command(name="enable", description="Enable pvp")
async def pvp_enable(interaction: discord.Interaction):
    await pvpAdmin.pvp_enable(interaction)

@pvpAdminGroup.command(name="disable", description="Disable pvp")
async def pvp_disable(interaction: discord.Interaction):
    await pvpAdmin.pvp_disable(interaction)

@pvpAdminGroup.command(name="add_loot_type", description="Add a loot type to the database")
async def add_loot_type(interaction: discord.Interaction, name: str, description: str, consumable: bool, attack_rarity: int, vc_rarity: int):
    await pvpAdmin.add_loot_type(interaction, name, description, consumable, attack_rarity, vc_rarity)

@pvpAdminGroup.command(name='fix_attack', description='Fix an attack in the database')
async def fix_attack(interaction: discord.Interaction, attack_id: Optional[int], attack_type: Optional[str], attack_description: Optional[str]):
    await pvpAdmin.fix_attack(interaction, attack_id, attack_type, attack_description)

@pvpAdminGroup.command(name='fix_defense', description='Fix a defense in the database')
async def fix_defense(interaction: discord.Interaction, attack_id: int, defense_description: str, winner_id: int):
    await pvpAdmin.fix_defense(interaction, attack_id, defense_description, winner_id)

@pvpAdminGroup.command(name='adjust_rarity', description='Adjust the rarity of a loot type')
async def adjust_rarity(interaction: discord.Interaction, loot_name: str, attack_rarity: int, vc_rarity: int):
    await pvpAdmin.adjust_rarity(interaction, loot_name, attack_rarity, vc_rarity)

@pvpAdminGroup.command(name="reset", description="Reset pvp and the database")
async def reset_pvp(interaction: discord.Interaction):
    await pvpAdmin.reset_pvp(interaction)

@tree.command(name='outro', description='Kick everyone from your current VC')
async def leaveVC(interaction: discord.Interaction):
    try:
        await leave.leaveVC(interaction)
    except Exception as e:
        await dmTyler(e)

####        Media Commands        ####
mediaGroup = app_commands.Group(name='alexa', description='Control Tymler\'s music capabilities')
@mediaGroup.command(name="play", description="Resume/Start playing media or add to the queue")
async def play(interaction: discord.Interaction, url: str = None):
    try:
        await media.play(interaction, url)
    except Exception as e:
        await dmTyler(e)

@mediaGroup.command(name='pause', description='Pause playing media')
async def pause(interaction: discord.Interaction):
    try:
        await media.pause(interaction)
    except Exception as e:
        await dmTyler(e)

@mediaGroup.command(name='stop', description='Stops whatever audio is playing')
async def stop(interaction: discord.Interaction):
    try:
        await media.stop(interaction)
    except Exception as e:
        await dmTyler(e)

@mediaGroup.command(name='skip', description='Skips to the next thing in the queue')
async def skip(interaction: discord.Interaction):
    try:
        await media.skip(interaction)
    except Exception as e:
        await dmTyler(e)

@mediaGroup.command(name="shuffle", description="Toggles shuffle for the queue. Shuffle turns off when the queue is empty")
async def shuffle(interaction: discord.Interaction):
    try:
        await media.shuffle(interaction)
    except Exception as e:
        await dmTyler(e)

@mediaGroup.command(name="help", description="Explains each media command")
async def help(interaction: discord.Interaction):
    try:
        await media.help(interaction)
    except Exception as e:
        await dmTyler(e)

####        Mention Commands        ####
mentionGroup = app_commands.Group(name='random', description='"@" a random person in the discord server')
@mentionGroup.command(name='mention', description='"@" a random person in the discord server')
async def mention(interaction: discord.Interaction):
    await mentionUser(interaction)

####        Bot Events        ####
## Detect when user enters vc ## 
@client.event
async def on_voice_state_update(member, before, after):
    await playSoundWhenTylerJoinsVC(member, before, after)

## Detect when a member is updated ##
@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    await forcePVPDeaths(before, after)

## Detect when a message is sent ##
@client.event
async def on_message(message):
    # try:
    #     await messageSent.enforceTheKellieRule(message)
    # except Exception as e:
    #     await dmTyler(f'Could not enforce The Kellie Rule: \n{e}')
    try:
        await messageSent.clientMentioned(message)
    except Exception as e: 
        await dmTyler(f'Could not respond to message:\n{e}')


## Start automatic tasks ##
@client.event
async def on_connect():
    print("Connected")
    client.loop.create_task(playRandomSoundLoop())
    client.loop.create_task(changeStatusLoop())

## Run Discord Client ##
@client.event
async def on_ready():
    tree.clear_commands(guild=None)
    tree.add_command(whitelist)
    tree.add_command(serverGroup)
    tree.add_command(roleGroup)
    tree.add_command(adminGroup)
    tree.add_command(mediaGroup)
    tree.add_command(mentionGroup)
    tree.add_command(jacobGroup)
    tree.add_command(pvpGroup)
    tree.add_command(pvpAdminGroup)
    tree.add_command(leaveVC)
    await tree.sync()
    
    await changeStatus()

    print("Ready")

globalVariables.client = client
client.run(TOKEN)
