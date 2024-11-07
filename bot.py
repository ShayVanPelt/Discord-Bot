import discord
import random
import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv(".env")
token: str = os.getenv("token")

#intents = discord.Intents.default()
intents = discord.Intents.all()

client = discord.Client(intents=intents)

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

con = None

async def print_users(message):
   async with con.cursor() as cursor:
        await cursor.execute('SELECT id, money FROM users')
        rows = await cursor.fetchall()
        results = "\n".join([f"User: {message.guild.get_member(row[0]).name}, Balance: ${row[1]}" for row in rows])
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

    if message.author.id == 799084628324778025:  #medha
        await message.channel.send("Hi Medha :)")

    if (msg[0] == '++help'):
        help_text = (
            "```All Current ShayBot Commands:\n"
            "++help - Show this help message with a list of commands\n"
            "++getbalance - Check your current balance, set initial balance, and reset balance if you get to $0\n"
            "++coinflip <heads/tails> <amount> - Bet on a coinflip with the specified amount and choice\n"
            "++table - Display the balance of all users\n"
            "++roulette <black/red/odd/even/(number 1 - 36)> <amount>```\n"
        )
        await message.channel.send(help_text)

    if (msg[0] == '++table'):
        await print_users(message)

    if (msg[0] == '++getbalance'):
        user_balance = await get_balance(message.author.id)
        if user_balance == 0:
            await set_balance(message.author.id, 100)
            await message.channel.send(f"{message.author.name}, your broke reset balance to: ${100}")
        else:
            await message.channel.send(f"{message.author.name}, your balance is: ${user_balance}")

    
    if (msg[0] == '++roulette' and len(msg) == 3):
        try:
            bet_amount = int(msg[2])  # Attempt to convert msg[2] to an integer
        except ValueError:
            await message.channel.send("Please choose a proper bet amount")
            return
        
        user_balance = await get_balance(message.author.id)
        if bet_amount > user_balance:
            await message.channel.send("Nice Try")
            return
        elif bet_amount <= 0:
            await message.channel.send("Nice Try")
            return
        
        try:
            bet = int(msg[1]) 
            if bet > 36 or bet < 1:
                await message.channel.send("Please choose a proper number in table (1 - 36)")
                return
            type = 0
        except ValueError:
            bet = msg[1]
            bet = bet.capitalize()
            if bet not in ["Red", "Black", "Odd", "Even"]:
                await message.channel.send("Please choose either 'Black' or 'Red' or 'Odd' or 'Even' or a number between 0 and 36.")
                return
            type = 1
        roll = random.randint(1, 36)  # Numbers from 1 to 36
        parity = "Even" if roll != 0 and roll % 2 == 0 else "Odd"
        if roll in RED_NUMBERS:
            color = "Red"
        elif roll in BLACK_NUMBERS:
            color = "Black"
        winnings = 0

        if bet in ["Red", "Black"]:
            if bet == color:
                winnings = bet_amount * 2
        elif bet in ["Even", "Odd"]:
            if bet == parity:
                winnings = bet_amount * 2
        else:
            if bet == roll:
                winnings = bet_amount * 36

        # Update balance based on winnings or loss
        if winnings > 0:
            new_balance = user_balance + winnings - bet_amount
            await set_balance(message.author.id, new_balance)
            await message.channel.send(
                f"The roulette landed on {roll} ({color}, {parity}).\n"
                f"You won ${winnings}! New balance: ${new_balance}."
            )
        else:
            new_balance = user_balance - bet_amount
            await set_balance(message.author.id, new_balance)
            await message.channel.send(
                f"The roulette landed on {roll} ({color}, {parity}).\n"
                f"You lost ${bet_amount}. New balance: ${new_balance}."
            )

    if (msg[0] == '++coinflip' and len(msg) == 3):
        try:
            bet_amount = int(msg[2])  # Attempt to convert msg[2] to an integer
        except ValueError:
            await message.channel.send("Please choose a proper int")
            return

        choice = msg[1].capitalize()

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
