import discord
import platform
import asyncio
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
        await play(interaction)
    except Exception as e:
        raise Exception(f"Failed to call play in joinVC\n{e}")
    return


async def play(interaction: discord.Interaction):
    botVC: discord.VoiceClient | None = interaction.guild.voice_client
    if botVC and botVC.is_playing():
        return
    if audioQueue:
        try:
            botVC.play(audioQueue.pop(0), after=lambda e: gv.client.loop.create_task(play(interaction)))
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