import discord
import asyncio
import botSupport.globalVariables
from botSupport.globalVariables import tylerUserID
from botSupport.botSounds import loadOpus

async def playSoundWhenTylerJoinsVC(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    client = botSupport.globalVariables.client
    if member.id == tylerUserID:
        if after.channel != None and before.channel == None:
            await after.channel.connect(timeout=30, reconnect=True)
            botVC = after.channel.guild.voice_client
            loadOpus()
            botVC.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('Sounds/Fanfare for a Clown.mp3'), volume=0.25), after=lambda e: asyncio.run_coroutine_threadsafe(botVC.disconnect(), client.loop))

        if before.channel != None and client.user in before.channel.members:
            botVC = before.channel.guild.voice_client
            botVC.stop()
            await botVC.disconnect()
    
    if before.channel != None and after.channel == None and client.user in before.channel.members and before.channel.guild.voice_client != None:
        botVC = before.channel.guild.voice_client
        botVC.stop()
        await botVC.disconnect()