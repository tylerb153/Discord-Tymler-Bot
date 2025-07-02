import discord
import random
from typing import Optional
from botSupport.databaseManager import DatabaseManager
from botSupport.commandGroups.pvp import dealDamage, giveLoot
import botSupport.globalVariables as gv
from botSupport.errorHandling import dmTyler
import re

async def pvp_enable(interaction: discord.Interaction):
    gv.pvp = True
    await interaction.response.send_message(content="@everyone PVP has been enabled.")

async def pvp_disable(interaction: discord.Interaction):
    gv.pvp = False
    await interaction.response.send_message(content="PVP has been disabled.")

async def add_loot_type(interaction: discord.Interaction, name: str, description: str, consumable: bool, attack_rarity: int, vc_rarity: int):
    pvpDatabase = DatabaseManager()
    pvpDatabase.addLootType(name, description, consumable, attack_rarity, vc_rarity)
    await interaction.response.send_message(content=f"{name} added to the database.")

async def fix_attack(interaction: discord.Interaction, attack_id: Optional[int], attack_type: Optional[str], attack_description: Optional[str]):
    interaction.response.defer(ephemeral=True)
    pvpDatabase = DatabaseManager()
    attacks = pvpDatabase.getAttacks()
    for attack in attacks:
        if attack.Type == "Pending":
            if attack_id == attack.AttackID and attack_type and attack_description:
                pvpDatabase.editAttack(attack, attack_type, attack_description)
                await interaction.edit_original_response(content=f"{attack} fixed")
                await interaction.channel.send(f'## <@{attack.AttackingUser.UserID}> attacked <@{attack.DefendingUser.UserID}>\n{attack_description}')
                break
            else:
                await interaction.edit_original_response(content=f"{attack}")

async def fix_defense(interaction: discord.Interaction, attack_id: int, defense_description: str, winner_id: int):
    interaction.response.defer(ephemeral=True)
    pvpDatabase = DatabaseManager()
    attacks = pvpDatabase.getAttacks()
    for attack in attacks:
        if attack.Winner == None and attack_id == attack.AttackID:
            pvpDatabase.editAttack(attack=attack, Winner=winner_id)
            await interaction.edit_original_response(content=f"{attack} fixed")
            await interaction.channel.send(content=f'## <@{attack.DefendingUser.UserID}>\'s defense against <@{attack.AttackingUser.UserID}>\n{defense_description}', silent=True)
            if winner_id == attack.AttackingUser.UserID:
                aoe = attack.Type == "AOE"
                membersAffected = [interaction.user]
                if aoe:
                    membersAffected.append(interaction.guild.get_member(attack.attackingUser.UserID))
                    membersAffected.append(random.choice(interaction.guild.members))
                    membersAffected.append(random.choice(interaction.guild.members))
                await dealDamage(interaction, membersAffected=membersAffected, pvpDatabase=pvpDatabase)
                msg = giveLoot(attackingUser=attack.AttackingUser, pvpDatabase=pvpDatabase, membersAffected=membersAffected)
                await interaction.channel.send(content=msg)
            break

async def adjust_rarity(interaction: discord.Interaction, loot_name: str, attack_rarity: int, vc_rarity: int):
    await interaction.response.defer(ephemeral=True)
    pvpDatabase = DatabaseManager()
    pvpDatabase.editRarity(loot_name, attack_rarity, vc_rarity)
    await interaction.edit_original_response(content=f"{loot_name} rarity adjusted")

async def reset_pvp(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    # Delete data in database
    DatabaseManager().reset()

    # Reset nicknames / remove roles
    members = interaction.guild.members
    for member in members:
        print(member.nick)
        try:
            nickname = member.nick
            if nickname and re.search(r' \d+$', nickname):
                nickname = re.sub(r' \d+$', '', nickname)
                await member.edit(nick=f'{nickname}')

            await member.remove_roles(discord.Object(id=gv.healthRoles[0]), discord.Object(id=gv.healthRoles[1]), discord.Object(id=gv.healthRoles[2]))

        except Exception as e:
            await dmTyler(f'Error reseting pvp: \n{e}')

    