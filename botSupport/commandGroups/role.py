import discord
import random
from botSupport.globalVariables import tylerUserID

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
