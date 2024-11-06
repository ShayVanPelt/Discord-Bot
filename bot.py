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

con = None

async def print_users(message):
    async with con.cursor() as cursor:
        await cursor.execute('SELECT id, money FROM users')
        rows = await cursor.fetchall()
        results = "\n".join([f"User ID: {message.guild.get_member(row[0]).name}, Balance: ${row[1]}" for row in rows])
        await message.channel.send(results)
        
async def set_balance(user_id, amount):
    async with con.cursor() as cursor:
        await cursor.execute('UPDATE users SET money = ? where id = ?', (amount, user_id))
        await con.commit()

async def get_balance(user_id):
    async with con.cursor() as cursor:
        await cursor.execute('SELECT money FROM users WHERE id = ?', (user_id,))
        result = await cursor.fetchone()
        if result is None:
            await cursor.execute('INSERT INTO users (id, money) VALUES (?, ?)', (user_id, 5000))
            await con.commit()
            return 5000
        else:
            await con.commit()
        return result[0]

#status=discord.Status.invisible,
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(' :)'))
    print(f'We have logged in as {client.user}')
    global con 
    con = await aiosqlite.connect("main.db")
    async with con.cursor() as cursor:
        await cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, money INTEGER)')
    await con.commit()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.split()

    if (msg[0] == '++table'):
        await print_users(message)

    if (msg[0] == '++getbalance'):
        user_balance = await get_balance(message.author.id)
        if user_balance == 0:
            await set_balance(message.author.id, 100)
            await message.channel.send(f"{message.author.name}, your broke reset balance to: ${100}")
        else:
            await message.channel.send(f"{message.author.name}, your balance is: ${user_balance}")

    if (msg[0] == '++coinflip' and len(msg) == 3):
        try:
            bet_amount = int(msg[1])  # Attempt to convert msg[1] to an integer
        except ValueError:
            await message.channel.send("Please choose a proper int")
            return

        choice = msg[2].capitalize()

        if choice not in ["Heads", "Tails"]:
            await message.channel.send("Please choose either 'heads' or 'tails' for the coinflip.")
            return
        
        user_balance = await get_balance(message.author.id)
        if bet_amount > user_balance:
            await message.channel.send("Nice Try")
            return
        elif bet_amount <= 0:
            await message.channel.send("Nice Try")
            return
    
        rand = random.choice(["Heads", "Tails"])
        if choice == rand:
            await set_balance(message.author.id, (user_balance + bet_amount))
            await message.channel.send(f"{rand}! You won ${bet_amount}. New balance: ${(user_balance + bet_amount)}")
        else:
            await set_balance(message.author.id, (user_balance - bet_amount))
            await message.channel.send(f"{rand}! You lost ${bet_amount}. New balance: ${(user_balance - bet_amount)}")



client.run(token)
