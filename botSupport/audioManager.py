import discord
import platform
import asyncio
from yt_dlp import YoutubeDL
import botSupport.globalVariables as gv

audioQueue = []

def loadOpus():
    if platform.system() == 'Darwin':
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')
    elif platform.system() == 'Linux':
        discord.opus.load_opus('libopus.so.0')

async def addAudio(interaction: discord.Interaction, audio: discord.FFmpegPCMAudio):
    try:
        audioQueue.append(audio)
    except Exception as e:
        raise Exception(f"Could not add audio to queue\n{e}")
    try:
        await joinVC(interaction)
    except Exception as e:
        raise Exception(f"Failed to call joinVC in addAudio\n{e}")

async def joinVC(interaction: discord.Interaction):
    botVC = interaction.guild.voice_client
    try:
        if botVC == None:
            loadOpus()
            botVC = interaction.user.voice.channel
            await botVC.connect(timeout=30, reconnect=True)
    except Exception as e:
        raise Exception(f"Failed to connect to the voice channel\n{e}")
    try:
        await asyncio.sleep(1)
        await play(interaction.guild.voice_client)
    except Exception as e:
        raise Exception(f"Failed to call play in joinVC\n{e}")
    return


async def play(botVC: discord.VoiceClient):
    if botVC and botVC.is_playing():
        return
    if audioQueue:
        audioTitle, audioURL = await asyncio.to_thread(getAudioStreamInfo, audioQueue.pop(0))
        try:
            await asyncio.sleep(1)
            botVC.play(discord.FFmpegPCMAudio(source=audioURL, options=f"-filter:a volume={0.25}"), after=lambda e: gv.client.loop.create_task(play(botVC)))
        except Exception as e:
            raise Exception(f"Failed to play audio in audioManager.play\n{e}")
        try:
            pass
            # Report what is playing
        except:
            pass
    else:
        await asyncio.sleep(1)
        await botVC.disconnect()
    
    return


def getAudioStreamInfo(url):
    if 'playlist' in url:
        # loop through the playlist, that's a problem for later fr fr
        return
    
    if 'youtu' in url:
        ydl_opts = {
            'outtmpl': 'Sounds/MediaTempFile/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url=url, download=False)
            info = ydl.sanitize_info(info)
            print(f'Playing URL: {info.get('url')}')
            return info.get('title'), info.get('url')
    return