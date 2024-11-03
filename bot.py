import discord
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


#status=discord.Status.invisible,
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('with your mom'))
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    msg2 = str(msg.lower())

    if message.author.id == 217143982105427968:  #Peter
        await message.channel.send("Peter is sexy")

    if message.author.id == 799084628324778025:  #medha
        await message.channel.send("Hi Medha :)")

    if 'fuck shay' in msg2:
        await message.channel.send("fuck " + message.author.name)

    if 'fuck mingo' in msg2:
        await message.channel.send("Facts")

    if 'fuck peter' in msg2:
        await message.channel.send("Not facts")

    if 'peter' in msg2:
        await message.channel.send("Peter is very sexy")

    if msg.startswith('++coinflip'):
        rand = random.choice(["Heads", "Tails"])
        await message.channel.send(rand)



client.run('KEY')
