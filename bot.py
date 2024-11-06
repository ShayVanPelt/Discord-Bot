import discord
import random
import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv(".env")
token: str = os.getenv("token")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


#status=discord.Status.invisible,
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(' :)'))
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('++coinflip'):
        rand = random.choice(["Heads", "Tails"])
        await message.channel.send(rand)




client.run(token)
