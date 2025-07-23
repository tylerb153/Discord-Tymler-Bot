import discord
import asyncio
import random
import botSupport.globalVariables as gv
from botSupport.botSounds import loadOpus

async def leaveVC(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # Join the vc the user is in.
    # Play the song
    # Get the list of the users also in that VC
    # disconnect all of them.
    
    channel = interaction.user.voice.channel

    loadOpus()
            
    if channel.guild.voice_client != None and channel.guild.voice_client.is_connected():
        botVC = channel.guild.voice_client
    else:
        await channel.connect(timeout=30, reconnect=True)
        botVC: discord.VoiceProtocol = channel.guild.voice_client
    
    await interaction.delete_original_response()

    vcMembers = channel.members
    # await botVC.play(discord.FFmpegPCMAudio("Sounds/Outro Music/Outro.mp3"))

    soundpath = "Sounds/Outro Music/"


    match (random.randint(1, 25)):
        case 1:
            soundpath += "Bass Boosted Outro.mp3"
            volumeLevel = 1
        case 2:
            soundpath += "Edging Outro.mp3"
            volumeLevel = .75
        case 3:
            await asyncio.sleep(3)
            await disconnectEveryone(vcMembers, botVC)
            return
        case 4:
            soundpath += "Echo Outro.mp3"
            volumeLevel = 0.75
        case 5:
            soundpath += "Shreksophone.mp3"
            volumeLevel = 0.75
        case 6:
            soundpath += "Awful Outro.mp3"
            volumeLevel = 1
        case 7:
            soundpath += "The beat dropped lmao.mp3"
            volumeLevel = 0.25
        case 8:
            soundpath += "TheFatRat - Xenogenesis (Outro Song).mp3"
            volumeLevel = 0.5
        case 9:
            soundpath += "Coconut Malled lmao.mp3"
            volumeLevel = 0.5
        case _:
            soundpath += "Outro.mp3"
            volumeLevel = 0.5

    botVC.play(discord.FFmpegPCMAudio(soundpath, options=f"-filter:a volume={volumeLevel}"), after=lambda e: asyncio.run_coroutine_threadsafe(disconnectEveryone(vcMembers, botVC), gv.client.loop))
    
    

async def disconnectEveryone(members: list[discord.Member], botVC: discord.VoiceProtocol):
    await botVC.disconnect()
    for member in members:
        if member != gv.client.user:
            await member.edit(voice_channel=None)
