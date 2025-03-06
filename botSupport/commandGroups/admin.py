import discord
import botSupport.globalVariables
from botSupport.errorHandling import dmTyler
from botSupport.globalVariables import tylerUserID
from botSupport.botSounds import playRandomSound

async def disconnect(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    client = botSupport.globalVariables.client
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    try:
        botVC: discord.VoiceClient = interaction.guild.voice_client
        await botVC.disconnect()
    except Exception as e:
        print(f'Exception occured in disconnect()\n{e}')
        await dmTyler(client, f'Exception occured in disconnect()\n{e}')
    await interaction.delete_original_response()

async def set_status(interaction: discord.Interaction, status: str):
    client = botSupport.globalVariables.client
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    await interaction.response.defer(ephemeral=True)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="The Minecraft Cult", state=status))
    await interaction.delete_original_response()

async def play_sound(interaction: discord.Interaction):
    if not interaction.user.id == tylerUserID:
        await interaction.edit_original_response(content="You do not have permission to use this command")
        return
    await interaction.response.defer(ephemeral=True)
    await playRandomSound(interaction.user.voice.channel)
    await interaction.delete_original_response()

