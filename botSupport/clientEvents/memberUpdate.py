import discord
import re
import botSupport.globalVariables
from botSupport.errorHandling import dmTyler
from botSupport.databaseManager import DatabaseManager

async def forcePVPDeaths(before: discord.Member, after: discord.Member):
    client = botSupport.globalVariables.client
    if after.nick == None and after.global_name != None:
            await after.edit(nick=after.global_name)
    elif after.nick == None and after.global_name == None:
            await after.edit(nick=after.name)
    if after != client.user and before.nick != after.nick:
        amountOfDeaths = int(DatabaseManager().getUser(after.id).AmountOfDeaths)
        if after.nick.endswith(f' {amountOfDeaths + 1}') or amountOfDeaths == 0:
            # await after.guild.get_channel(785666938276675624).send(content=f'{after.mention} :eyes:')
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{after.nick} change thier name.', state=f'👀👀👀👀'))
        else:
            try:
                newNick = after.nick
                if re.search(r' \d+$', after.nick):
                    newNick = re.sub(r' \d+$', '', newNick)
                await after.edit(nick=f'{newNick} {amountOfDeaths + 1}')
            except Exception as e:
                await dmTyler(client, f'Failed to edit nick in on_member_update I was trying to change it to **{after.nick} {amountOfDeaths + 1}**:\n{e}')
    