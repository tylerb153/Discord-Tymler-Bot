import discord
import re
import botSupport.audioManager as audioManager
import botSupport.globalVariables as gv

async def play(interaction: discord.Interaction, url = str|None):
    await interaction.response.defer()
    userVC = interaction.user.voice
    botVC: discord.VoiceClient = interaction.guild.voice_client
    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
    
    elif url == None and botVC and botVC.is_paused():
        botVC.resume()
        await interaction.edit_original_response(content=f'Resuming audio!')
    
    elif url == None and botVC and not botVC.is_paused():
        await interaction.edit_original_response(content=f'Audio is playing already. Enter a url to queue something')
    
    elif url and (botVC == None or botVC.channel == userVC.channel):
        if re.search(pattern="(https://)?youtu.be*", string=url) != None or re.search(pattern="(https://www.)?youtube.com/watch\?*", string=url) != None or re.search(pattern="(https://www.)?youtube.com/playlist\?*", string=url) != None:
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

async def pause(interaction: discord.Interaction):
    await interaction.response.defer()
    userVC = interaction.user.voice
    botVC: discord.VoiceClient | None = interaction.guild.voice_client
    
    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
    elif botVC == None:
        await interaction.edit_original_response(content=f'I\'m not in a vc... You woke me from my nap {interaction.user.mention} 😡')
    elif botVC.channel == userVC.channel:
        if botVC.is_playing():
            try:
                audioManager.pause(botVC)
            except Exception as e:
                await interaction.edit_original_response(content=f'I failed to pause the audio playing!')
                raise Exception(f"Failed to pause music in media.pause\n{e}")
            await interaction.edit_original_response(content=f'Paused the audio playing!')
        elif botVC.is_paused():    
            await interaction.edit_original_response(content=f'Audio is already paused I can\'t pause it harder!')
        else:
            await interaction.edit_original_response(content=f'I\'m not playing anything that I can pause!')
    else:
        await interaction.edit_original_response(content=f'We aren\'t in the same vc so stop bothering me ☹️')
    
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    userVC = interaction.user.voice
    botVC: discord.VoiceClient | None = interaction.guild.voice_client

    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
    elif botVC == None:
        await interaction.edit_original_response(content=f'I\'m not in a vc... what am I even supposed to stop?')
    elif botVC.channel == userVC.channel:
        try:
            audioManager.stop(botVC)
        except Exception as e:
                await interaction.edit_original_response(content=f'I failed to stop the audio playing!')
                raise Exception(f"Failed to stop music in media.stop\n{e}")
        await interaction.edit_original_response(content=f'Stopped the audio playing!')
    else:
        await interaction.edit_original_response(content=f'We aren\'t in the same vc 🙄')

async def skip(interaction: discord.Interaction):
    await interaction.response.defer()
    userVC = interaction.user.voice
    botVC: discord.VoiceClient | None = interaction.guild.voice_client

    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
    elif botVC == None:
        await interaction.edit_original_response(content=f'You tell me what I\'m supposed to skip and I\'ll do it!')
    elif botVC.channel == userVC.channel:
        try:
            await audioManager.skip(botVC)
        except Exception as e:
                await interaction.edit_original_response(content=f'I failed to skip the audio playing!')
                raise Exception(f"Failed to skip music in media.skip\n{e}")
        await interaction.edit_original_response(content=f'Skipped the audio playing!')
    else:
        await interaction.edit_original_response(content=f'We aren\'t in the same vc... just tell me you hate me next time 😔')

async def shuffle(interaction: discord.Interaction):
    await interaction.response.defer()
    userVC = interaction.user.voice
    botVC: discord.VoiceClient | None = interaction.guild.voice_client

    if not userVC:
        await interaction.edit_original_response(content=f'You are not in a voice channel!')
    elif botVC == None:
        await interaction.edit_original_response(content=f'I can\'t skip nothing 🙄')
    elif botVC.channel == userVC.channel:
        try:
            audioManager.shuffleAudio()
        except Exception as e:
                await interaction.edit_original_response(content=f'I failed to activate shuffle!')
                raise Exception(f"Failed to skip music in media.skip\n{e}")
        if audioManager.shuffle:
            await interaction.edit_original_response(content=f'Activated shuffle!')
        else:
            await interaction.edit_original_response(content=f'Deactivated shuffle!')
    else:
        await interaction.edit_original_response(content=f'We aren\'t in the same vc... just tell me you hate me next time 😔')