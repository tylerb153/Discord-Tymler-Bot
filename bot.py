import asyncio
import time
from typing import Optional
import discord
from discord import app_commands
from discord import FFmpegPCMAudio
from discord import ui
from mcrcon import MCRcon #mcrcon is used to create a remote console to your minecraft server
import yt_dlp
import requests
import random
import dotenv
import os
import subprocess
import platform
import json
import databaseManager
from databaseManager import DatabaseManager

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

guild = discord.Object(id=554203267001745419)
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

## User ID ##
tylerUserID = 336959815374864384 #Used in multiple commands

## Health Roles ##
healthRoles = [1308398348918718474, 1308398507727786054, 1308398555622408255]

@tree.command(name='whitelist', description='Add your minecraft username to the whitelist')
async def whitelist(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    print(username)
    finalmsg = f'{username} was added to the whitelist' #adds usrname and has been added to the varible finalmsg
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
            await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="Cult 3.0 Members"))
        else:
            raise Exception('The minecraft server may not be running')
    except Exception as e:
        await dmTyler(f'An error occured in the whitelist command with error:\n{e}')
        print(f'An error occured in the whitelist command with error:\n{e}')
        finalmsg = f'I couldn\'t add **{username}** :sob: and have notified <@{tylerUserID}>'

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
            if not interaction.user.id == tylerUserID:
                await dmTyler(":rotating_light: The Minecraft Cult Server is Offline! WEEE WOOO WEEE WOOO :rotating_light:")
            await interaction.edit_original_response(content=f":red_circle: The Minecraft Cult Server is Offline! :(")
    else:
        print(f"API call to {url} failed with status code {response.status_code}.")
        await dmTyler(f"API call to {url} failed with status code {response.status_code}.")
        await interaction.edit_original_response(content=":warning: Could not check for online status")

@serverGroup.command(name="start", description="If the minecraft server is down start it.")
async def start(interaction: discord.Interaction):
    await interaction.response.defer()
    # await interaction.edit_original_response(content="There is no active Minecraft server at this time the Minecraft Cult 2.5 server is shut down.")
    # return
    try:
        if await getServerRunning():
            await interaction.edit_original_response(content="The server is already running, use **/server status** to check 😜")
        else:
            ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("SSH_HOSTNAME")}', f'nohup bash {os.getenv("SSH_SCRIPT_PATH")}/serverStart.sh > /dev/null 2>&1 &']
            subprocess.run(ssh_command, capture_output=False, text=True)
            await interaction.edit_original_response(content="The server is starting please don't panic and cry!")
    except Exception as e:
        print(f'An error occured in the start command with error:\n{e}')
        await dmTyler(f'An error occured in the start command with error:\n{e}')
        await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't start the server :sob:")


jacobGroup = app_commands.Group(name="jacob", description="Commands for Jacob")
@jacobGroup.command(name="skitzing", description="Title and subtitle for minecraft server... HUH?!")
async def skitzing(interaction: discord.Interaction, title: str, subtitle: str = ""):
    await interaction.response.defer(ephemeral=True)
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
    except Exception as e:
        print(f'An error occured in the skitzing command with error:\n{e}')
        await dmTyler(f'An error occured in the skitzing command with error:\n{e}')
    
    await interaction.delete_original_response()


adminGroup = app_commands.Group(name="admin", description="Commands that only the admins can use")
@adminGroup.command(name="stop", description="If the minecraft server is running stop it.")
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

@adminGroup.command(name='backup', description='Backs up the minecraft server')
async def backup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    try:
        if await getServerRunning():
            ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("SSH_HOSTNAME")}', f'nohup echo {os.getenv("SSH_PASSWORD")} | sudo -S bash {os.getenv("SSH_SCRIPT_PATH")}/serverSave.sh > /dev/null 2>&1 &']
            subprocess.run(ssh_command, capture_output=False, text=True)
            await interaction.edit_original_response(content="The server is saving!")
        else:
            await interaction.edit_original_response(content="The server not running so it won't be backed up!")
    except Exception as e:
        print(f'An error occured in the backup command with error:\n{e}')
        await dmTyler(f'An error occured in the backup command with error:\n{e}')
        await interaction.edit_original_response(content=f"<@{tylerUserID}> I couldn't backup the server :sob:")


@adminGroup.command(name='disconnect', description='Disconnects the bot from the voice channel')
async def disconnect(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    try:
        botVC: discord.VoiceClient = interaction.guild.voice_client
        await botVC.disconnect()
    except Exception as e:
        print(f'Exception occured in disconnect()\n{e}')
        await dmTyler(f'Exception occured in disconnect()\n{e}')
    await interaction.delete_original_response()

@adminGroup.command(name='set_status', description='Sets the status of the bot')
async def set_status(interaction: discord.Interaction, status: str):
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    await interaction.response.defer(ephemeral=True)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="The Minecraft Cult", state=status))
    await interaction.delete_original_response()

@adminGroup.command(name='play_sound', description='Plays a sound from the SoundEffects folder')
async def play_sound(interaction: discord.Interaction):
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    await interaction.response.defer(ephemeral=True)
    await playRandomSound(interaction.user.voice.channel)
    await interaction.delete_original_response()

@adminGroup.command(name="op", description="Gives user operator privliges")
async def op(interaction: discord.Interaction, username: str):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    resp = ""
    try:    
        if (await getServerRunning()):
            with MCRcon(os.getenv('MINECRAFT_SERVER_IP_ADDRESS'), os.getenv('RCON_PASSWORD')) as mcr:
                resp = mcr.command(f'/op {username}')
                await interaction.edit_original_response(content=resp)
        else:
            raise Exception('There is a problem with the minecraft server or op command')
    except Exception as e:
        print(f'An error occured in the op command with error:\n{e}')
        await dmTyler(f'An error occured in the op command with error:\n{e}')
        await interaction.edit_original_response(content=f"I couldn't give operator privliges to {username} :sob:")
    
    
    

roleGroup = app_commands.Group(name='role', description='Manages user roles')

@roleGroup.command(name='add', description='Assigns a role with chosen name and color. Defaults to random color. Accepts hex or Discord colors.')
async def add(interaction: discord.Interaction, name: str, color: str = ""):
    await interaction.response.defer(ephemeral=True)
    color = getColor(color)
    customRoleDividerName = "TymlerBot" #Look at making this dynamic
    nameStripped = name.strip('/@&<>')

    if name == '@everyone':
        await interaction.edit_original_response(content=f'You have @everyone by default :man_facepalming:', allowed_mentions=False)
        return
    
    bannedRoles = getBannedRoles(interaction)
    # print(bannedRoles.keys())
    # print(nameStripped)
    if nameStripped in str(bannedRoles.keys()) or name in bannedRoles.values():
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

pvpGroup = app_commands.Group(name='pvp', description='PVP other discord members')

@pvpGroup.command(name="attack", description="Attack a member and describe how you attacked them.")
async def attack(interaction: discord.Interaction, defender: discord.Member):
    if not interaction.guild:
        await interaction.response.send_message(content=f'You cannot use pvp commands in a DM chat', ephemeral=True)
        return
    
    # if defender == interaction.user:
    #     await interaction.response.send_message(content="You can't attack yourself 🤦", ephemeral=True)
    #     return

    if defender == client.user:
        await interaction.response.defer(ephemeral=True)
        #TODO: Contact GPT for a defence that wins everytime and sends that
        await interaction.edit_original_response(content="You can't attack me I am a ***GOD*** here")
        return
    
    pvpDatabase = DatabaseManager()
    attacks = pvpDatabase.getAttacks()
    attackingUser = pvpDatabase.getUser(interaction.user.id)
    defendingUser = pvpDatabase.getUser(defender.id)
    for attack in attacks:
        if attackingUser == attack.AttackingUser and defendingUser == attack.DefendingUser and attack.Complete == False:
            await interaction.response.send_message(content=f'You are already attacking {defender.mention}. Wait until they defend your current attack', ephemeral=True)
            return
        
    class attackModal(discord.ui.Modal):
        def __init__(self, title: str, defendingUser: databaseManager.User):
            super().__init__(title=title)
            self.defendingUser = defendingUser
            self.add_item(ui.TextInput(label="Describe your attack", placeholder="Description of your attack", style=discord.TextStyle.paragraph))
            
        async def on_submit(self, interaction: discord.Interaction):
            await preformAttack(interaction, self.defendingUser)

    await interaction.response.send_modal(attackModal(f'{interaction.user.nick}\'s attack', defendingUser))
    del pvpDatabase
    

async def preformAttack(interaction: discord.Interaction, defendingUser: databaseManager.User):
    #TODO Contact chatGPT for attack summary and type, should return object {attackType: "Single Target/AOE", Description: "description"}"
    
    response = json.loads('{"AttackType": "AOE", "Description": "Under the cover of chaos, the hero tore apart an old microwave, yanking out the magnetron and rigging it into a makeshift energy weapon using stripped wires, a broken drone battery, and a shattered binocular lens to focus the beam. As the enemy closed in, they flipped the jerryrigged device on, unleashing a searing pulse of concentrated microwaves that superheated metal and fried electronics in a crackling burst of destruction. Each blast from the improvised weapon sent waves of devastation through the ranks, leaving a smoking path of victory in its wake."}')
    pvpDatabase = DatabaseManager()
    pvpDatabase.createAttack(attackingUser=pvpDatabase.getUser(interaction.user.id), defendingUser=defendingUser, Type=response['AttackType'], attackDescription=response['Description'])
    del pvpDatabase
    
    await interaction.response.send_message(content=f"## {interaction.user.mention} attacked {interaction.guild.get_member(defendingUser.UserID)}\n{response['Description']}")

@pvpGroup.command(name="defend", description="Defend a member's attack and describe how you defended them.")
async def defend(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.edit_original_response(content=f'You cannot use pvp commands in a DM chat')
        return
    
    pvpDatabase = DatabaseManager()
    defendingUser = pvpDatabase.getUser(interaction.user.id)
    

    class DefendButton(ui.Button):
        def __init__(self, label:str, originalInteraction:discord.Interaction, attackToDefend:databaseManager.Attack):
            super().__init__(label=label, style=discord.ButtonStyle.red)
            self.originalInteraction = originalInteraction
            self.attackToDefend = attackToDefend

        async def callback(self, interaction: discord.Interaction):
            await self.originalInteraction.delete_original_response()
            return await presentDefendModal(interaction, self.attackToDefend)
        
    class DefendDropdown(ui.Select):
        def __init__(self, options:list[discord.SelectOption] , originalInteraction:discord.Interaction):
            super().__init__(options=options)
            self.originalInteraction = originalInteraction

        async def callback(self, interaction: discord.Interaction):
            await self.originalInteraction.delete_original_response()
            # print(interaction.data['values'])
            await presentDefendModal(interaction, DatabaseManager().getAttack(int(interaction.data['values'][0])))
        
    view = ui.View()
    attacksParagraph = '## Attacks against you!\n'
    attacksAgainstDefender:list[databaseManager.Attack] = []
    for attack in pvpDatabase.getAttacks():
        if attack.DefendingUser == defendingUser and not attack.Complete:
            attacksAgainstDefender.append(attack)
            attacksParagraph += f'- <@{attack.AttackingUser.UserID}> - {attack.Description}\n'
    if len(attacksAgainstDefender) == 0:
        await interaction.edit_original_response(content="Nobody is attacking you right now 😄\n Go make some enemies now 😈")
    elif len(attacksAgainstDefender) == 1:
        view.add_item(DefendButton(label="Defend this attack", originalInteraction=interaction, attackToDefend=attacksAgainstDefender[0]))
        await interaction.edit_original_response(content=attacksParagraph, view=view)
    else:
        options = []
        for attack in attacksAgainstDefender:
            options.append(discord.SelectOption(label=interaction.guild.get_member(attack.AttackingUser.UserID).nick, value=attack.AttackID))
        view.add_item(DefendDropdown(options, originalInteraction=interaction))
        attacksParagraph += "\nSelect an attacker to defend against:"
        await interaction.edit_original_response(content=attacksParagraph, view=view)

    del pvpDatabase

async def presentDefendModal(interaction: discord.Interaction, attackToDefend:databaseManager.Attack):
    class defenceModal(discord.ui.Modal):
        def __init__(self, title: str, attackToDefend: databaseManager.Attack):
            super().__init__(title=title)
            self.attackToDefend = attackToDefend
            self.add_item(ui.TextInput(label="Describe your defence", placeholder="Description of your defence", style=discord.TextStyle.paragraph))
            
        async def on_submit(self, interaction: discord.Interaction):
            await preformDefense(interaction, self.attackToDefend)

    await interaction.response.send_modal(defenceModal(title=f'Defend against {interaction.guild.get_member(attackToDefend.AttackingUser.UserID).nick}', attackToDefend=attackToDefend))

async def preformDefense(interaction: discord.Interaction, currentAttack:databaseManager.Attack):
    # print("preforming defense")
    await interaction.response.defer()
    attackingUser = currentAttack.AttackingUser
    defendingUser = currentAttack.DefendingUser
    pvpDatabase = DatabaseManager()
    # preform the defense
        #TODO contact gpt and get a defense

    response = json.loads('{"SuccessfulAttack": "True", "AOEDamage": "True", "Description": "Anticipating the swing, the cornered warrior ducked just as the chair splintered against the wall behind them, dodging the blow with a smirk. They rolled to the side, grabbing their comically large hammer—nearly twice their own height—and hoisted it with a theatrical flourish. With a grunt, they brought it down in a slow, exaggerated arc, forcing their opponent to scramble away, tripping over the debris in a desperate bid to avoid the absurdly oversized weapon."}')

    await interaction.followup.send(content=f'## <@{defendingUser.UserID}>\'s defense against <@{attackingUser.UserID}>\n{response["Description"]}', silent=True)
    await asyncio.sleep(15)
    if response['SuccessfulAttack'] == "True":
        # Remove health from affected users
        aoe = response['AOEDamage']
        membersAffected = [interaction.user]
        if aoe:
            membersAffected.append(interaction.guild.get_member(attackingUser.UserID))
            membersAffected.append(random.choice(interaction.guild.members))
            membersAffected.append(random.choice(interaction.guild.members))
        for member in membersAffected:
            user = pvpDatabase.getUser(member.id)
            newHealth = user.Health - 1
            if newHealth <= 0:
                newHealth = 3
                pvpDatabase.updateDeaths(user, user.AmountOfDeaths + 1)
            pvpDatabase.updateHealth(user, newHealth)
            user = pvpDatabase.getUser(user.UserID)
            match int(user.Health):
                case 1:
                    await member.add_roles(discord.Object(id=healthRoles[0]))
                    await member.remove_roles(discord.Object(id=healthRoles[1]))
                    await member.remove_roles(discord.Object(id=healthRoles[2]))
                case 2:
                    await member.add_roles(discord.Object(id=healthRoles[0]))
                    await member.add_roles(discord.Object(id=healthRoles[1]))
                    await member.remove_roles(discord.Object(id=healthRoles[2]))
                case _: #3 or higher adds all three health roles
                    await member.add_roles(discord.Object(id=healthRoles[0]))
                    await member.add_roles(discord.Object(id=healthRoles[1]))
                    await member.add_roles(discord.Object(id=healthRoles[2]))
        defendingUser = pvpDatabase.getUser(defendingUser.UserID)
        
        

        # Give attacker loot
        msg = f'## <@{attackingUser.UserID}>\'s attack was successful and they gain\n'
        lootList = pvpDatabase.getLootTable()
        lootGained = {}
        for loot in lootList:
            if loot.attackRarity > 0 and random.randint(1, 100) <= loot.attackRarity:
                lootGained.update({loot: 1})
        pvpDatabase.giveLoot(attackingUser, lootGained)

        if lootGained == []:
            msg += "- Nothing\n"
        else:
            for loot in lootGained:
                msg += f'- {loot.Name}\n'

        msg += f'\n'
        for member in membersAffected:
            user = pvpDatabase.getUser(member.id)
            msg += f'\n<@{user.UserID}> is now at {user.Health} Health and {user.AmountOfDeaths} Deaths'
        await interaction.channel.send(content=f"{msg}")

        pvpDatabase.completeAttack(currentAttack, attackingUser)
    else:
        # Attack Failed
        pvpDatabase.completeAttack(currentAttack, defendingUser)
        await interaction.followup.send(content=f'## {interaction.user.mention}\'s defense was successful they take no damage\n\n<@{defendingUser.UserID}> is now at {defendingUser.Health} Health and {defendingUser.AmountOfDeaths} Deaths')
    
    del pvpDatabase


@pvpGroup.command(name='health', description='Check someone\'s health')
async def health(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.edit_original_response(content=f'You cannot use pvp commands in a DM chat')
        return
    
    pvpDatabase = DatabaseManager()
    if not member:
        member = interaction.user
    user = pvpDatabase.getUser(member.id)
    await interaction.edit_original_response(content=f'<@{user.UserID}> is at {user.Health} Health and {user.AmountOfDeaths} Deaths')
    del pvpDatabase

@pvpGroup.command(name="battles", description='List all previous battle from person')
async def battles(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.edit_original_response(content=f'You cannot use pvp commands in a DM chat')
        return
    
    pvpDatabase = DatabaseManager()
    if not member:
        member = interaction.user
    user = pvpDatabase.getUser(member.id)
    attacks = pvpDatabase.getAttacks()
    msg = f'## {member.mention}\'s Previous Battles:\n**Attacker v. Defender**\n'
    for attack in attacks:
        if attack.AttackingUser == user or attack.DefendingUser == user:
            if attack.Winner:
                msg += f'<@{attack.AttackingUser.UserID}> v. <@{attack.DefendingUser.UserID}> - Winner: <@{attack.Winner.UserID}>\n'
            else:
                msg += f'<@{attack.AttackingUser.UserID}> v. <@{attack.DefendingUser.UserID}> - Winner: *In progress*\n'

    await interaction.edit_original_response(content=msg)
    del pvpDatabase

@pvpGroup.command(name="inventory", description="Show items or use an item")
async def inventory(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.edit_original_response(content=f'You cannot use pvp commands in a DM chat')
        return
    
    pvpDatabase = DatabaseManager()
    user = pvpDatabase.getUser(interaction.user.id)

    class ItemSelect(ui.Select):
        def __init__(self, options, originalInteraction:discord.Interaction):
            super().__init__(placeholder="Select an item to use", options=options)
            self.originalInteraction = originalInteraction
        async def callback(self, interaction: discord.Interaction):
            await item_selected(interaction, originalInteraction=self.originalInteraction)
    view = ui.View()
    inventoryParagraph = ''
    lootOptions = []
    for loot, amount in user.Inventory.items():
        inventoryParagraph += f'{loot.Name}: {amount} -- *{loot.Description}*\n'
        lootOptions.append(loot)

    options = []
    for loot in lootOptions:
        options.append(discord.SelectOption(label=loot.Name, value=loot.Name))
    selection = ItemSelect(options=options, originalInteraction=interaction)
    
    if lootOptions == []:
        await interaction.edit_original_response(content=f"You have no items in your inventory.", view=view)
    else:
        view.add_item(selection)
        await interaction.edit_original_response(content=f"{inventoryParagraph}\n", view=view)
        
    del pvpDatabase

async def item_selected(interaction: discord.Interaction, originalInteraction: discord.Interaction):
    await originalInteraction.delete_original_response()
    pvpDatabase = DatabaseManager()
    user = pvpDatabase.getUser(interaction.user.id)
    lootRemoved = None
    for loot in pvpDatabase.getLootTable():
        if loot.Name == interaction.data['values'][0]:
            lootRemoved = loot
            break
    try:
        pvpDatabase.useLoot(user, lootRemoved)
        await interaction.channel.send(content=f"{interaction.user.mention} used a {interaction.data['values'][0]}")
    except Exception as e:
        print(e)
        await dmTyler(f"Using an item failed with error:\n{e}")
        await originalInteraction.followup.send(f'{interaction.user.mention} I\'m sorry but you cannot use your {lootRemoved.Name}!', ephemeral=True)
        del pvpDatabase
     
#TODO: Make multipage for items
@pvpGroup.command(name="help", description="Show help for pvp commands")
async def pvp_help(interaction: discord.Interaction):
    await interaction.response.send_message(ephemeral=True, content=

f'''
# PvP Help Menu

## Attack
- **Command:** `/pvp attack <defender>`
- **Description:** Initiates an attack on the specified member of the server. You will be prompted to describe your attack, which will then create an ongoing battle between you and the defender.
- **Example:** `/pvp attack` {interaction.user.mention}

**Notes:**
- Only one active attack on a defender is allowed.


## Defend
- **Command:** `/pvp defend`
- **Description:** Displays all active attacks against you and allows you to defend against one. If you choose to defend, you’ll be prompted to submit a description of your defense.
- **Example:** `/pvp defend`

**Notes:**
- If successful, you take no damage; otherwise, you lose health and potentially die.
- A failed defense might also damage other members in an AOE attack.


## Health
- **Command:** `/pvp health <member>`
- **Description:** Displays the health and number of deaths for yourself or another server member.
- **Example:** `/pvp health` or `/pvp health` {interaction.user.mention}


## Battles
- **Command:** `/pvp battles <member>`
- **Description:** Lists all previous battles involving the specified member, showing outcomes and participants.
- **Example:** `/pvp battles` or `/pvp battles` {client.user.mention}


## Inventory
- **Command:** `/pvp inventory`
- **Description:** Shows your inventory of items and allows you to use them. Each item has unique effects.
- **Example:** `/pvp inventory`

**Usage:**
1. Use `/pvp inventory` to view all items in your inventory.
2. Select an item to use it.

## Help
- **Command:** `/pvp help`
- **Description:** Displays this help menu.

## When You Die:
1. Your health is reset to **3** upon death, allowing you to "respawn" and continue participating in PvP.
2. Your server nickname is updated to reflect your total number of deaths, adding 1 to your current count.

''')

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

mentionGroup = app_commands.Group(name='random', description='"@" a random person in the discord server')
@mentionGroup.command(name='mention', description='"@" a random person in the discord server')
async def mention(interaction: discord.Interaction):
    await interaction.response.defer()
    chosenPerson = random.choice(interaction.guild.members)
    await interaction.edit_original_response(content=f'{chosenPerson.mention}')

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
    customRoleDividerName = 'TymlerBot'
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

async def getServerRunning() -> bool:
    ssh_command = ['ssh', f'{os.getenv("SSH_USERNAME")}@{os.getenv("SSH_HOSTNAME")}', f'bash {os.getenv("SSH_SCRIPT_PATH")}/serverStatus.sh']

    try:
        # raise Exception("Testing wooooo")
        result = subprocess.run(ssh_command, capture_output=True, text=True)
        print(result)

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
        await dmTyler(f'Exeption occured while running ssh command in getServerRunning()\n{e}')
        raise e

def loadOpus():
    if platform.system() == 'Darwin':
                discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.1/lib/libopus.0.dylib')
    elif platform.system() == 'Linux':
        discord.opus.load_opus('libopus.so.0')

def getSounds(folderPath: str, soundList: list) -> list:
    for i in os.listdir(folderPath):
        fullPath = os.path.join(folderPath, i)
        if os.path.isfile(fullPath):
            soundList.append(fullPath)
        else:
            getSounds(fullPath, soundList)
        
    return soundList

def getSpecialAvatar(sound: str) -> Optional[str]:
    nickname = None
    match sound:
        case 'SoundEffects/Minecraft Movie/I..... AM STEVE.mp3':
            nickname = 'Steve'
        case 'SoundEffects/Minecraft Movie/Minecraft Movie Sheep.mp3':
            nickname = 'Sheep'
    return nickname

async def playRandomSound(channel: discord.VoiceChannel):
    loadOpus()
    sounds = getSounds('SoundEffects/', [])
    # sounds = ['SoundEffects/Minecraft Movie/I..... AM STEVE.mp3', 'SoundEffects/Minecraft Movie/Minecraft Movie Sheep.mp3']
    randomSound = random.choice(sounds)
    nickname = getSpecialAvatar(randomSound)
    previousNickname = channel.guild.me.nick
    if nickname != None:
        await channel.guild.me.edit(nick=nickname)

    if channel.guild.voice_client != None and channel.guild.voice_client.is_connected():
        botVC = channel.guild.voice_client
    else:
        await channel.connect(timeout=30, reconnect=True)
        botVC = channel.guild.voice_client
    
    if nickname != None:
        async def cleanup(previousNickname):
            await botVC.disconnect()
            await channel.guild.me.edit(nick=previousNickname)
        botVC.play(FFmpegPCMAudio(randomSound), after=lambda e: client.loop.create_task(cleanup(previousNickname)))

    else:
        botVC.play(FFmpegPCMAudio(randomSound), after=lambda e: asyncio.run_coroutine_threadsafe(botVC.disconnect(), client.loop))

async def dmTyler(message: str):
    try:
        channel = await client.create_dm(discord.Object(id=tylerUserID))
        await channel.send(content=message)
    except Exception as e:
        print(f'Could not dm Tyler: \n{e}')

## End of Helper Functions ##

## Detect when user enters vc ## 
@client.event
async def on_voice_state_update(member, before, after):
    if member.id == tylerUserID:
        if after.channel != None and before.channel == None:
            await after.channel.connect(timeout=30, reconnect=True)
            botVC = after.channel.guild.voice_client
            loadOpus()
            botVC.play(discord.PCMVolumeTransformer(FFmpegPCMAudio('Fanfare for a Clown.mp3'), volume=0.25), after=lambda e: asyncio.run_coroutine_threadsafe(botVC.disconnect(), client.loop))

        if before.channel != None and client.user in before.channel.members:
            botVC = before.channel.guild.voice_client
            botVC.stop()
            await botVC.disconnect()
    
    if before.channel != None and after.channel == None and client.user in before.channel.members and before.channel.guild.voice_client != None:
        botVC = before.channel.guild.voice_client
        botVC.stop()
        await botVC.disconnect()

## Detect when a member is updated ##
@client.event
async def on_member_update(before, after):
    if after != client.user and before.nick != after.nick:
        await after.guild.get_channel(785666938276675624).send(content=f'{after.mention} :eyes:')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{after.nick} change thier name.', state=f'👀👀👀👀'))
    
## Detect when a message is sent ##
@client.event
async def on_message(message):
    # print(message)
    if message.author == client.user:
        return
    meMentioned = False
    if client.user in message.mentions:
        meMentioned = True

    ## Process message to change 'y' to 'ie' ##
    messages = message.content.split(" ")
    userString = ""
    messageChanged = False
    for word in messages:
        def removeY(word) -> str:
            nonlocal messageChanged    
            if word.endswith('y'):
                word = word[:-1] + 'ie'
                messageChanged = True
            if word.endswith('Y'):
                word = word[:-1] + 'IE'
                messageChanged = True
            return word
        def removePunctuationThenConvert(word: str) -> str:
            punctuation = '*~`!@#$%^&()_+={}[]|\\;\'"<>,?/.-1234567890'
            if word[-1] in punctuation:
                return removePunctuationThenConvert(word[:-1]) + word[-1]
            else:
                return removeY(word)
        if "y" in word or "Y" in word:
            word = removePunctuationThenConvert(word)
            
        userString += word + " "
        
    if messageChanged:
        await message.delete()
        if message.type == discord.MessageType.reply:
            message = await (await message.channel.fetch_message(message.reference.message_id)).reply(content=userString + f" - {message.author.mention}")
        else:
            message = await message.channel.send(userString + f" - {message.author.mention}")

    if meMentioned:
        with open('mentionResponses.txt', 'r') as file:
            responses = file.readlines()
            randomResponse = random.choice(responses).strip()
            await message.reply(content=f'{randomResponse}')


async def changeStatus():
    with open('statuses.txt', 'r') as file:
        statuses = file.readlines()
        randomStatus = random.choice(statuses).strip()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="The Minecraft Cult", state=randomStatus))

 
## Play Random Sounds ##
async def playRandomSoundLoop():
    while not client.is_closed():
        await asyncio.sleep(random.randint(10, 7200))
        print("Playing random sound")
        for guild in client.guilds:
            activeVoiceChannels = [vc for vc in guild.voice_channels if len(vc.members) > 0]
            if activeVoiceChannels:
                randomChannel = random.choice(activeVoiceChannels)
                await playRandomSound(randomChannel)

async def changeStatusLoop():
    while not client.is_closed():
        await asyncio.sleep(random.randint(10, 3600))
        print("Changing status")
        await changeStatus()

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
    # tree.add_command(mediaGroup)
    tree.add_command(adminGroup)
    tree.add_command(mentionGroup)
    tree.add_command(jacobGroup)
    tree.add_command(pvpGroup)
    await tree.sync()
    await changeStatus()
    print("Ready")



client.run(TOKEN)

