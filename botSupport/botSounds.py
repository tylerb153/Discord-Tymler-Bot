import discord
import os
import platform
import asyncio
import random
import ctypes.util
from typing import Optional
import botSupport.globalVariables

async def playRandomSoundLoop():
    client = botSupport.globalVariables.client
    while not client.is_closed():
        await asyncio.sleep(random.randint(300, 10800))
        print("Playing random sound")
        for guild in client.guilds:
            activeVoiceChannels = [vc for vc in guild.voice_channels if len(vc.members) > 0]
            if activeVoiceChannels:
                randomChannel = random.choice(activeVoiceChannels)
                await playRandomSound(randomChannel)

def loadOpus():
    if platform.system() == 'Darwin':
                discord.opus.load_opus('/opt/homebrew/Cellar/opus/1.5.2/lib/libopus.0.dylib')
    elif platform.system() == 'Linux':
        discord.opus.load_opus('libopus.so.0')


def getSounds(folderPath: str, soundList: list) -> list:
    for i in os.listdir(folderPath):
        fullPath = os.path.join(folderPath, i)
        if os.path.isfile(fullPath):
            soundList.append(fullPath)
        else:
            getSounds(fullPath, soundList)
        
    return soundList

def getSpecialAvatar(sound: str) -> Optional[str]:
    nickname = None
    match sound:
        case 'Sounds/SoundEffects/Minecraft Movie/I..... AM STEVE.mp3':
            nickname = 'Steve'
        case 'Sounds/SoundEffects/Minecraft Movie/Minecraft Movie Sheep.mp3':
            nickname = 'Sheep'
    return nickname

async def playRandomSound(channel: discord.VoiceChannel):
    client = botSupport.globalVariables.client
    loadOpus()
    sounds = getSounds('Sounds/SoundEffects/', [])
    # sounds = ['SoundEffects/Minecraft Movie/I..... AM STEVE.mp3', 'SoundEffects/Minecraft Movie/Minecraft Movie Sheep.mp3']
    randomSound = random.choice(sounds)
    nickname = getSpecialAvatar(randomSound)
    previousNickname = channel.guild.me.nick
    if nickname != None:
        await channel.guild.me.edit(nick=nickname)

    if channel.guild.voice_client != None and channel.guild.voice_client.is_connected():
        botVC = channel.guild.voice_client
    else:
        await channel.connect(timeout=30, reconnect=True)
        botVC = channel.guild.voice_client
    
    asyncio.sleep(2)

    if nickname != None:
        async def cleanup(previousNickname):
            await botVC.disconnect()
            await channel.guild.me.edit(nick=previousNickname)
        botVC.play(discord.FFmpegPCMAudio(randomSound), after=lambda e: client.loop.create_task(cleanup(previousNickname)))

    else:
        botVC.play(discord.FFmpegPCMAudio(randomSound), after=lambda e: asyncio.run_coroutine_threadsafe(botVC.disconnect(), client.loop))
