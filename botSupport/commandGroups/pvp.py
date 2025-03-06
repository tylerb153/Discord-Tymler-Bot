import discord
from discord import ui
import random 
import json
import asyncio
import re
import botSupport.databaseManager as databaseManager
from botSupport.databaseManager import DatabaseManager
from botSupport.openai_yapping import OpenAiYapper
import botSupport.globalVariables as gv
from botSupport.globalVariables import tylerUserID, healthRoles
from botSupport.errorHandling import dmTyler, log

async def attack(interaction: discord.Interaction, defender: discord.Member):
    if not interaction.guild:
        await interaction.response.send_message(content=f'You cannot use pvp commands in a DM chat', ephemeral=True)
        return
    if gv.pvp == False:
        await interaction.response.send_message(content=f'PVP is currently disabled', ephemeral=True)
        return
    
    # if defender == interaction.user:
    #     await interaction.response.send_message(content="You can't attack yourself 🤦", ephemeral=True)
    #     return
    
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
            self.attackDescription = ui.TextInput(label="Describe your attack", placeholder="Description of your attack", style=discord.TextStyle.paragraph)
            self.add_item(self.attackDescription)
            
        async def on_submit(self, interaction: discord.Interaction):
            # print(interaction.data)
            await preformAttack(interaction, self.defendingUser, self.attackDescription.value)

    await interaction.response.send_modal(attackModal(f'{interaction.user.nick}\'s attack', defendingUser))
    await updateHealthRoles(interaction.user)
    await updateHealthRoles(defender)
    del pvpDatabase
    

async def preformAttack(interaction: discord.Interaction, defendingUser: databaseManager.User, attackDescription: str):
    client = gv.client
    # {"Attacker": "Name", "Defender": "Name", "Description": "attack description"}
    #{"AttackType": "AOE", "Description": "`Your Description of the battle`"}
    if not interaction.response.is_done():
        await interaction.response.defer(thinking=True)

    if interaction.guild.get_member(defendingUser.UserID) == client.user or defendingUser.UserID == 1314736871594528829:
            response = "You can't attack me I am a ***GOD*** here"
            randomMember = random.choice(interaction.guild.members)
            try:
                ai = OpenAiYapper("You are the character Tymler. You are a robot but you don't know it and you never mention it but you will sometimes let mannerisms through, you believe you are the god of the realm The Minecraft Cult. You believe youhave complete control over what happens in your realm. You are an agent of chaos and abide by the rule that funny ≠ random. The peasants in the realm worship you and do your bidding. You have commanded they fight each other for your amusement. Now they have risen up against you. Here is a description of thier attack as \"god\" of the realm make it known you're god by providing a defense against thier attack that would never fail and demand forcefully the attacker fight another one of the peasents name this peasent \"{peasent}\". Keep your defense to 5 sentences")
                response = ai.chat([attackDescription])
                log(response)
                response = response.replace("{peasent}", randomMember.mention)
            except Exception as e:
                print(f'Failed to chat in preformAttack:\n{e}')
                await dmTyler(f'Failed to chat with openai in preformAttack:\n{e}\nAi response:\n{response}')
            
            response += f"\n\n{interaction.user.mention} loses 1 Healh"
            await interaction.channel.send(content=response, silent=True)
            await dealDamage(interaction, [interaction.user], DatabaseManager())
            await preformAttack(interaction=interaction, client=client, defendingUser=DatabaseManager().getUser(randomMember.id), attackDescription=attackDescription)
            return

    pvpDatabase = DatabaseManager()
    attacker = pvpDatabase.getUser(interaction.user.id)

    ai = OpenAiYapper(
'''
You are a dungeons and dragons DM and are overseeing battles between two group members. Your job is to take the description of what the attacker would like to do and turn it into an epic attack against their opponent. Even if the attacker says their attack lands it has NOT yet you ARE NOT allowed to mention calls on whether the attack lands EVER. You will be given the attacker's name, the defender's name, and the description of what the attacker wants to accomplish in an object that looks like this:
{"Attacker": "Name", "Defender": "Name", "Description": "attack description", "AttackerStats": ("Strength: int", "Dexterity: int", "Intelligence: int", "Charisma: int")}

You need to take this information and turn it into a 3 sentence attack scene. This scene SHOULD NOT include who wins or loses just what the attack is. NEVER mention how or if the attack lands or a winner. Your description MUST be leave room for the defender to defend themselves. The Defense and decision is supplied by someone else.
You decide how the attack is preformed taking into account the stats of the attacker. for example a low strength attacker that wants to throw a rock might throw a smaller one then a high strength. All Stats are on a scale of 1 - 10
You need to decide what type of attack this is. There are two types, `Single Target`, or `AOE`. If you believe the attack would have an large enough of an area effect then it is an AOE attack. This shouldn't be easy but require a sufficiently broad attack.

Once you have an attack and description return this information in a json object with this pattern. All "'" characters need to be escaped like this "\\'":
{"AttackType": "AOE", "Description": "Your Description of the attack"}
''')
    aiResponse = ''
    response = json.loads('{"AttackType": "AOE", "Description": "Under the cover of chaos, the hero tore apart an old microwave, yanking out the magnetron and rigging it into a makeshift energy weapon using stripped wires, a broken drone battery, and a shattered binocular lens to focus the beam. As the enemy closed in, they flipped the jerryrigged device on, unleashing a searing pulse of concentrated microwaves that superheated metal and fried electronics in a crackling burst of destruction. Each blast from the improvised weapon sent waves of devastation through the ranks, leaving a smoking path of victory in its wake."}')
    try:
        # print(attackDescription)
        if interaction.user.nick == None:
            await interaction.user.edit(nick=interaction.user.name)

        aiResponse = ai.chat([f'{{"Attacker": "{interaction.user.nick}", "Defender": "{interaction.guild.get_member(defendingUser.UserID).nick}", "Description": "{attackDescription}", "AttackerStats": ("Strength: {attacker.Strength}", "Dexterity: {attacker.Dexterity}", "Intelligence: {attacker.Intelligence}", "Charisma: {attacker.Charisma}")}}', "Remember do not under any circumstances mentions who wins, or if the attack lands. You are a DM and you are supposed to be explaining the attack. So the Defender can specify thier defense"])
        log(aiResponse)
        response = json.loads(aiResponse)
    except Exception as e:
        print(f'Error in preform attack: \n{e}')
        attackCreated = pvpDatabase.createAttack(attackingUser=attacker, defendingUser=defendingUser, Type="Pending", attackDescription=f"<@{tylerUserID}> is fixing this attack")
        log(attackCreated)
        await interaction.edit_original_response(content=f'Could not preform the attack something went horribly wrong! <@{tylerUserID}> will fix your attack please hold!')
        await dmTyler(f'Error in preform attack: \n{e}\nattackDescription:\n{attackDescription}\naiResponse:\n{aiResponse}\nAttack Created: f{attackCreated}')
        del pvpDatabase
        return
    
    pvpDatabase.createAttack(attackingUser=attacker, defendingUser=defendingUser, Type=response['AttackType'], attackDescription=response['Description'])
    del pvpDatabase
    
    await interaction.delete_original_response()
    await interaction.channel.send(content=f"## {interaction.user.mention} attacked {interaction.guild.get_member(defendingUser.UserID).mention}\n{response['Description']}")

async def defend(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await updateHealthRoles(interaction.user)
    if gv.pvp == False:
        await interaction.edit_original_response(content=f'PVP is currently disabled')
        return
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
        if attack.DefendingUser == defendingUser and not attack.Complete and attack.Type != "Pending":
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
            if len(options) > 3:
                break
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
            self.selection = ui.TextInput(label="Describe your defence", placeholder="Description of your defence", style=discord.TextStyle.paragraph)
            self.add_item(self.selection)
            
        async def on_submit(self, interaction: discord.Interaction):
            await preformDefense(interaction, self.attackToDefend, self.selection.value)

    await interaction.response.send_modal(defenceModal(title=f'Defend against {interaction.guild.get_member(attackToDefend.AttackingUser.UserID).nick}', attackToDefend=attackToDefend))

async def preformDefense(interaction: discord.Interaction, currentAttack:databaseManager.Attack, defenseDescription:str):
    # print("preforming defense")
    await interaction.response.defer(thinking=True)
    client = gv.client
    await updateHealthRoles(interaction.user)
    attackingUser = currentAttack.AttackingUser
    defendingUser = currentAttack.DefendingUser
    pvpDatabase = DatabaseManager()
    # preform the defense
    ai = OpenAiYapper(
'''
You are a dungeons and dragons DM and are overseeing battles between two group members. Your job is to take the description of what the defender would like to do and turn it into an epic defence against their opponent's attack. You will be given the attacker's name, the defender's name, and the description of what the defender wants to do in order to defend the attack in an object that looks like this:
{"Attacker": "Name", "Defender": "Name", "Attack": "attack description", "DefenseDescription": "how defender would like to defend against taking damage", "AttackerStats": ("Strength: int", "Dexterity: int", "Intelligence: int", "Charisma: int"), DefenderStats": ("Strength: int", "Dexterity: int", "Intelligence: int", "Charisma: int")}

You need to take this information and turn it into a 3 sentence defense scene. This scene SHOULD NOT include who wins or loses just what the defense is. This is purely a defense absolutely NO counterattacks. You should determine whether or not the attack is a success it shouldn't be too easy to defend an attack the defender may not have the skill to pull of the move they'd like it is up to you to decide if they do. If the defender isn't damaged this is a failed attack and SuccessfulAttack is false. If the defender does take damage SuccessfulAttack is True
You decide how the defense is preformed taking into account the stats of the attacker and defender. for example a low strength defender may struggle to block a high strength attacker using an attack that requires a high strength. All Stats are on a scale of 1 - 10

Always return the defense you came up with in a json object with this pattern. All "'" characters need to be escaped like this "\\'":
{"SuccessfulAttack":"True", "Description": "Your Description of the defense"}

''')

    aiResponse = ""
    response = json.loads('{"SuccessfulAttack": "True", "Description": "Anticipating the swing, the cornered warrior ducked just as the chair splintered against the wall behind them, dodging the blow with a smirk. They rolled to the side, grabbing their comically large hammer—nearly twice their own height—and hoisted it with a theatrical flourish. With a grunt, they brought it down in a slow, exaggerated arc, forcing their opponent to scramble away, tripping over the debris in a desperate bid to avoid the absurdly oversized weapon."}')
    try:
        if interaction.user.nick == None:
            await interaction.user.edit(nick=interaction.user.name)
        aiResponse = ai.chat([f'{{"Attacker": "{interaction.guild.get_member(attackingUser.UserID).nick}", "Defender": "{interaction.guild.get_member(defendingUser.UserID).nick}", "Attack": "{currentAttack.Description}", "DefenseDescription": "{defenseDescription}", "AttackerStats": ("Strength: {attackingUser.Strength}", "Dexterity: {attackingUser.Dexterity}", "Intelligence: {attackingUser.Intelligence}", "Charisma: {attackingUser.Charisma}"), "DefenderStats": ("Strength: {defendingUser.Strength}", "Dexterity: {defendingUser.Dexterity}", "Intelligence: {defendingUser.Intelligence}", "Charisma: {defendingUser.Charisma}")}}'])
        log(aiResponse)
        response = json.loads(aiResponse)
    except Exception as e:
        print(f'Error in preform defense: \n{e}')
        await interaction.edit_original_response(content=f'Could not preform the defense something went horribly wrong! <@{tylerUserID}> will fix your defense please hold!')
        await dmTyler(f'Error in preform defense: \n{e}\ndefenseDescription:\n{defenseDescription}\naiResponse:\n{aiResponse}\nDefending against{currentAttack}')
        pvpDatabase.completeAttack(currentAttack, None)
        del pvpDatabase
        return

    await interaction.channel.send(content=f'## <@{defendingUser.UserID}>\'s defense against <@{attackingUser.UserID}>\n{response["Description"]}', silent=True)
    await asyncio.sleep(5)
    if response['SuccessfulAttack'] == "True":
        # Remove health from affected users
        aoe = currentAttack.Type == "AOE"
        membersAffected = [interaction.user]
        if aoe:
            membersAffected.append(interaction.guild.get_member(attackingUser.UserID))
            while len(membersAffected) < 4:
                randomMember = random.choice(interaction.guild.members)
                if randomMember != client.user:
                    membersAffected.append(randomMember)
        msg = giveLoot(attackingUser, pvpDatabase, membersAffected)
        await dealDamage(interaction, membersAffected, pvpDatabase)
        defendingUser = pvpDatabase.getUser(defendingUser.UserID)
        msg += f'\n'
        for member in membersAffected:
            user = pvpDatabase.getUser(member.id)
            msg += f'\n<@{user.UserID}> is now at {user.Health} Health and {user.AmountOfDeaths} Deaths'
        
        await interaction.delete_original_response()
        await interaction.channel.send(content=f"{msg}")

        pvpDatabase.completeAttack(currentAttack, attackingUser)
    else:
        # Attack Failed
        pvpDatabase.completeAttack(currentAttack, defendingUser)
        await interaction.delete_original_response()
        await interaction.channel.send(content=f'## {interaction.user.mention}\'s defense was successful they take no damage\n\n<@{defendingUser.UserID}> has {defendingUser.Health} Health and {defendingUser.AmountOfDeaths} Deaths')
    
    del pvpDatabase

async def dealDamage(interaction: discord.Interaction, membersAffected: list[discord.Member], pvpDatabase: DatabaseManager):
    client = gv.client
    for member in membersAffected:
            if member == client.user:
                continue
            user = pvpDatabase.getUser(member.id)
            newHealth = user.Health
            #use a forcefield if a user has one
            try:
                usedForcefield = False
                for loot in user.Inventory:
                    if loot.Name == 'Forcefield':
                        forcefieldToRemove = loot
                        await interaction.channel.send(content=f'{member.mention} used a {loot.Name}', silent=True)
                        pvpDatabase.removeLoot(user, forcefieldToRemove)
                        usedForcefield = True
                        break
                if not usedForcefield:
                    newHealth = user.Health - 1
            except:
                newHealth = user.Health - 1
            if newHealth <= 0:
                newHealth = 3
                #Use a totem of undying if a user has one
                try:
                    usedTotem = False
                    for loot in user.Inventory:
                        if loot.Name == 'Totem of Undying':
                            totemToRemove = loot
                            await interaction.channel.send(content=f'{member.mention} used a {loot.Name}', silent=True)
                            usedTotem = True
                            pvpDatabase.removeLoot(user, totemToRemove)
                            break
                    if not usedTotem:
                        pvpDatabase.updateDeaths(user, user.AmountOfDeaths + 1)
                        pvpDatabase.updateUserStats(user, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
                except Exception as e:
                    await dmTyler(f"I ran into a problem with the totem of undying\n{e}")
                    pvpDatabase.updateDeaths(user, user.AmountOfDeaths + 1)
                    pvpDatabase.updateUserStats(user, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
                
                user = pvpDatabase.getUser(user.UserID)
                try:
                    newNick = f'{member.nick} {user.AmountOfDeaths + 1}'
                    if re.search(r' \d+$', member.nick):
                        newNick = re.sub(r' \d+$', '', newNick)
                    await member.edit(nick=f'{newNick}')
                except Exception as e:
                    await dmTyler(f'Failed to edit nick in on_member_update I was trying to change it to **{member.nick} {user.AmountOfDeaths + 1}**:\n{e}')
            pvpDatabase.updateHealth(user, newHealth)
            await updateHealthRoles(member)

async def updateHealthRoles(member: discord.Member):
    client = gv.client
    if member == client.user:
        return
    match int(DatabaseManager().getUser(member.id).Health):
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
    
def giveLoot(attackingUser: databaseManager.User, pvpDatabase: DatabaseManager, membersAffected: list[discord.Member]) -> str:
    msg = f'## <@{attackingUser.UserID}>\'s attack was successful and they gain\n'
    lootList = pvpDatabase.getLootTable()
    lootGained = {}
    for loot in lootList:
        if loot.attackRarity > 0 and random.randint(1, 100) <= loot.attackRarity:
            if loot.Name == "Gold":
                lootGained.update({loot: random.randint(1, 25)})
            else:
                lootGained.update({loot: 1})
    pvpDatabase.giveLoot(attackingUser, lootGained)

    if lootGained == {}:
        msg += "- Nothing\n"
    else:
        for loot in lootGained:
            msg += f'- {loot.Name}\n'

    return msg

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

async def battles(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.edit_original_response(content=f'You cannot use pvp commands in a DM chat')
        return
    
    pvpDatabase = DatabaseManager()
    if not member:
        member = interaction.user
    user = pvpDatabase.getUser(member.id)
    attacks = sorted(pvpDatabase.getAttacks(), key=lambda x: x.Winner is None, reverse=True)
    msg = f'## {member.mention}\'s Previous Battles:\n**Attacker v. Defender**\n'
    battlesInSet = 0
    for attack in attacks:
        if battlesInSet == 20:
            break
        if attack.AttackingUser == user or attack.DefendingUser == user:
            battlesInSet += 1
            if attack.Winner:
                msg += f'<@{attack.AttackingUser.UserID}> v. <@{attack.DefendingUser.UserID}> - Winner: <@{attack.Winner.UserID}>\n'
            else:
                msg += f'<@{attack.AttackingUser.UserID}> v. <@{attack.DefendingUser.UserID}> - Winner: *In progress*\n'

    await interaction.edit_original_response(content=msg)
    del pvpDatabase

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
        if amount == 0:
            continue
        inventoryParagraph += f'{loot.Name}: {amount} -- *{loot.Description}*\n'
        lootOptions.append(loot)

    options = []
    for loot in lootOptions:
        if loot.Consumable:
            options.append(discord.SelectOption(label=loot.Name, value=loot.Name))
    selection = ItemSelect(options=options, originalInteraction=interaction)
    
    if options:
        view.add_item(selection)
        await interaction.edit_original_response(content=f"{inventoryParagraph}\n", view=view)
    elif lootOptions:
            await interaction.edit_original_response(content=f"{inventoryParagraph}\n")
    else:
        await interaction.edit_original_response(content=f"You have no items in your inventory.", view=view)
        
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
        user = pvpDatabase.useLoot(user, lootRemoved)
        if lootRemoved.Name == "Health Potion":
            await updateHealthRoles(interaction.user)
            await interaction.channel.send(content=f'{interaction.user.mention} used a Health Potion. They now have {user.Health} Health')
        else:
            await interaction.channel.send(content=f"{interaction.user.mention} used a {interaction.data['values'][0]}")
        
        del pvpDatabase
    except Exception as e:
        print(e)
        await dmTyler(f"Using an item failed with error:\n{e}")
        await originalInteraction.followup.send(f'{interaction.user.mention} I\'m sorry but you cannot use your {lootRemoved.Name}!', ephemeral=True)
        del pvpDatabase
     
async def stats(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if not interaction.guild:
        await interaction.edit_original_response(content=f'You cannot use pvp commands in a DM chat')
        return
    
    pvpDatabase = DatabaseManager()
    user = pvpDatabase.getUser(interaction.user.id)
    await interaction.edit_original_response(content=f'# Your Stats:\n- Strength - {user.Strength}\n- Dexterity - {user.Dexterity}\n- Intelligence - {user.Intelligence}\n- Charisma - {user.Charisma}')
    del pvpDatabase

#TODO: Add Totem of undying
async def pvp_help(interaction: discord.Interaction):
    client = gv.client
    await interaction.response.send_message(ephemeral=True, content=

f'''
# PvP Help Menu

## Attack
- **Command:** `/pvp attack <defender>`
- **Description:** Initiates an attack on the specified member of the server. You will be prompted to describe your attack, which will then create an ongoing battle between you and the defender.
- **Example:** `/pvp attack` {client.user.mention}

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
- **Example:** `/pvp health` or `/pvp health` {client.user.mention}


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
- **Description:** Displays this help menu and the list of items

## When You Die:
1. Your health is reset to **3** upon death, allowing you to "respawn" and continue participating in PvP.
2. Your server nickname is updated to reflect your total number of deaths, adding 1 to your current count.

''')

    await interaction.followup.send(ephemeral=True, content=
f'''
## Items
- **Gold:**: Is shiny.
### Consumables
- **Health Potion:**: Restores 1 Health.
- **Steroids**: Adds 1 Strength
- **Weed**: Adds 1 Charisma
- **Shrooms**: Adds 1 Intelligence
- **Potion of Swiftness**: Adds 1 Dexterity

### Passive Effects
- **Totem of Undying**: When you die the totem takes your place. 
- **Forcefield**: You won't take damage the next time you are hit.
'''
    )
