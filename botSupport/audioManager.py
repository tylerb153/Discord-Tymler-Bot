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
    audioQueue.append(audio)
    await joinVC(interaction)

async def joinVC(interaction: discord.Interaction):
    botVC = interaction.guild.voice_client
    if botVC == None:
        loadOpus()
        botVC = interaction.user.voice.channel
        await botVC.connect(timeout=30, reconnect=True)
    await play(interaction)
    return


async def play(interaction: discord.Interaction):
    botVC = interaction.guild.voice_client

    if audioQueue:
        botVC.play(audioQueue.pop(0), after=lambda e: gv.client.loop.create_task(play(interaction)))
    else:
        await botVC.disconnect()
    
    return