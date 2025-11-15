import discord
import re
import botSupport.audioManager as audioManager

async def play(interaction: discord.Interaction, url = str|None):
    await interaction.response.defer()
    userVC = interaction.user.voice
    botVC: discord.VoiceClient = interaction.guild.voice_client
    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
    
    elif url == None and botVC and botVC.is_paused():
        botVC.resume()
        await interaction.edit_original_response(content=f'Resuming audio')
    
    elif url == None and botVC and not botVC.is_paused():
        await interaction.edit_original_response(content=f'Audio is playing already. Enter a url to queue something')
    
    elif url and (botVC == None or botVC.channel == interaction.user.voice.channel):
        if re.search(pattern="(https://)?youtu.be*", string=url) != None or re.search(pattern="(https://www.)?youtube.com/watch\?*", string=url) != None:
            try:
                await audioManager.addAudio(interaction, url)
            except Exception as e:
                await interaction.edit_original_response(content="Failed to add audio to the queue. I'm sorry :sob:")
                raise Exception(f"Failed to call addAudio\n{e}")
        else:
            await interaction.edit_original_response(content=f'{url} is not a valid url and cannot be added to the queue 🫣')
            return
        await interaction.edit_original_response(content=f'Added {url} to the queue!')
    else:
        await interaction.edit_original_response(content="Please provide a url to begin playing audio")
    return

