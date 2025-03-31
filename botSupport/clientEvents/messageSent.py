import discord
import random
import botSupport.globalVariables

async def enforceTheKellieRule(message: discord.Message):
    client = botSupport.globalVariables.client
    ## Process message to change 'y' to 'ie' ##
    # Also handles client mentions do to having to reply to a modified message
    # print(message)
    if message.author == client.user or message.channel.id in [1081167754746408960, 1228410126281740349]:
        return
    meMentioned = False
    if client.user in message.mentions:
        meMentioned = True

    ## Process message to change 'y' to 'ie' ##
    messages = message.content.split(" ")
    userString = ""
    messageChanged = False
    for word in messages:
        def removeY(word) -> str:
            nonlocal messageChanged    
            if word.endswith('y'):
                word = word[:-1] + 'ie'
                messageChanged = True
            if word.endswith('Y'):
                word = word[:-1] + 'IE'
                messageChanged = True
            return word
        def removePunctuationThenConvert(word: str) -> str:
            punctuation = '*~`!@#$%^&()_+={}[]|\\;\'"<>,?/.-1234567890'
            if word[-1] in punctuation:
                return removePunctuationThenConvert(word[:-1]) + word[-1]
            else:
                return removeY(word)
        if "y" in word or "Y" in word:
            word = removePunctuationThenConvert(word)
            
        userString += word + " "
        
    if messageChanged:
        await message.delete()
        if message.type == discord.MessageType.reply:
            message = await (await message.channel.fetch_message(message.reference.message_id)).reply(content=userString + f" - {message.author.mention}")
        else:
            message = await message.channel.send(userString + f" - {message.author.mention}")

    if meMentioned:
        with open('mentionResponses.txt', 'r') as file:
            responses = file.readlines()
            randomResponse = random.choice(responses).strip()
            await message.reply(content=f'{randomResponse}')



## Unused: Handled by enforceTheKellieRule ##
async def clientMentioned(message: discord.Message):
    client = botSupport.globalVariables.client
    if message.author == client.user:
        return
    
    if client.user in message.mentions:
        with open('botSupport/mentionResponses.txt', 'r') as file:
            responses = file.readlines()
            randomResponse = random.choice(responses).strip()
            await message.reply(content=f'{randomResponse}')