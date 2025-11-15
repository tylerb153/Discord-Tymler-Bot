import discord
import platform
import asyncio
from yt_dlp import YoutubeDL
from botSupport.botStatus import changeStatus
import botSupport.globalVariables as gv
from botSupport.errorHandling import dmTyler

audioQueue = []

def loadOpus():
    if platform.system() == 'Darwin':
        discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')
    elif platform.system() == 'Linux':
        discord.opus.load_opus('libopus.so.0')

async def addAudio(interaction: discord.Interaction, url: str):
    try:
        if 'list' in url:
            await asyncio.to_thread(processPlaylist, url)
        else:
            audioQueue.append(url)
    except Exception as e:
        raise Exception(f"Could not add audio to queue\n{e}")
    try:
        gv.client.loop.create_task(joinVC(interaction))
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
        gv.client.loop.create_task(play(interaction.guild.voice_client))
    except Exception as e:
        raise Exception(f"Failed to call play in joinVC\n{e}")
    return


async def play(botVC: discord.VoiceClient):
    if botVC and botVC.is_playing():
        return
    if audioQueue:
        audioTitle, audioURL = await asyncio.to_thread(getAudioStreamInfo, audioQueue.pop(0))
        
        try:
            gv.pauseRandomEvents = True
            print(f'Changing Status to {audioTitle}')
            await gv.client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name="The Minecraft Cult", state=f'Listening to {audioTitle}'))
        except Exception as e:
            await dmTyler(f'Failed to change presence in audioManager.play\n{e}')
        
        try:
            await asyncio.sleep(1)
            botVC.play(discord.FFmpegPCMAudio(source=audioURL, options=f"-filter:a volume={0.25}"), after=lambda e: gv.client.loop.create_task(play(botVC)))
        except Exception as e:
            raise Exception(f"Failed to play audio in audioManager.play\n{e}")
    else:
        await asyncio.sleep(1)
        gv.pauseRandomEvents = False
        await changeStatus()
        await botVC.disconnect()


def getAudioStreamInfo(url):
    if 'youtu' in url:
        # These options aren't necessary
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

def processPlaylist(url):
    ydl_opts = {
            'extract_flat': True,
            'ignoreerrors': True,
        }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                audioQueue.append(entry['url'])
        else:
            audioQueue.append(url)

def pause(botVC: discord.VoiceClient):
    botVC.pause()

async def stop(botVC: discord.VoiceClient):
    await botVC.disconnect()
    global audioQueue
    audioQueue = []

async def skip(botVC: discord.VoiceClient):
    await botVC.stop()
    await play(botVC)