import discord
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
        await interaction.edit_original_response(content=f'Added {url} to the queue!')
        try:
            await audioManager.addAudio(interaction, discord.FFmpegPCMAudio('Sounds/Look Ma No Hands! Leonard Bernstein at his best....mp3'))    
        except Exception as e:
            await interaction.edit_original_response(content="Failed to add audio to the queue. I'm sorry :sob:")
            raise Exception(f"Failed to call addAudio \n{e}")
    else:
        await interaction.edit_original_response(content="Please provide a url to begin playing audio")
    return
    
    # get youtube audio and send to queue

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

# @mediaGroup.command(name='leave', description='Force the bot to leave the channel at all costs')
async def leave(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        botVC: discord.VoiceClient = interaction.guild.voice_client
        await botVC.disconnect()
        await interaction.edit_original_response(content=(f'Disconnected myself successfully'))
    except Exception as e:
        await interaction.edit_original_response(content=f'Could not disconnect')
        print(f'Could not disconnect voice client in {interaction.guild.name}: {interaction.guild.id}\n{e}')

# @mediaGroup.command(name='stop', description='Stops playing audio')
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

# @mediaGroup.command(name='pause', description='Pauses playing audio')
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

