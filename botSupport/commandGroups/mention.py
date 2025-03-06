import discord
import random

async def mention(interaction: discord.Interaction):
    await interaction.response.defer()
    chosenPerson = random.choice(interaction.guild.members)
    await interaction.edit_original_response(content=f'{chosenPerson.mention}')