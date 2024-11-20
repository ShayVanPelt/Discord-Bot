import discord
from discord import app_commands
from discord.ext import commands
import random
import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv(".env")
token: str = os.getenv("token")

#intents = discord.Intents.default()
intents = discord.Intents.all()


client = commands.Bot(command_prefix="!",intents=intents)

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

con = None
        
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


@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} command(s): {[command.name for command in synced]}")
        await client.change_presence(activity=discord.Game(' Use /help'))
        global con 
        con = await aiosqlite.connect("main.db")
        async with con.cursor() as cursor:
            await cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, money INTEGER)')
        await con.commit()
    except Exception as e:
        print(e)


@client.tree.command(name="coinflip", description = "Flip Coin")
@app_commands.describe(choice = "Heads or Tails", bet = "Amount")
async def coinflip(interaction: discord.Interaction, choice: str, bet: int):
    try:
        bet_amount = int(bet)  
    except ValueError:
            await interaction.response.send_message("Please choose a proper int")
            return
    choice = choice.capitalize()
    if choice not in ["Heads", "Tails"]:
        await interaction.response.send_message("Please choose either 'heads' or 'tails' for the coinflip.")
        return
    user_balance = await get_balance(interaction.user.id)
    if bet_amount > user_balance:
        await interaction.response.send_message("Nice Try")
        return
    elif bet_amount <= 0:
        await interaction.response.send_message("Nice Try")
        return
    rand = random.choice(["Heads", "Tails"])
    if choice == rand:
        await set_balance(interaction.user.id, (user_balance + bet_amount))
        await interaction.response.send_message(f"{rand}! You won ${bet_amount}. New balance: ${(user_balance + bet_amount)}")
    else:
        await set_balance(interaction.user.id, (user_balance - bet_amount))
        await interaction.response.send_message(f"{rand}! You lost ${bet_amount}. New balance: ${(user_balance - bet_amount)}")


@client.tree.command(name="roulette", description = "Play Roulette")
@app_commands.describe(choice = "black/red/green/odd/even/(number 0 - 36)", bet = "Amount")
async def roulette(interaction: discord.Interaction, choice: str, bet: int):
    try:
        bet_amount = int(bet)  
    except ValueError:
        await interaction.response.send_message("Please choose a proper bet amount")
        return
        
    user_balance = await get_balance(interaction.user.id)
    if bet_amount > user_balance:
        await interaction.response.send_message("Nice Try")
        return
    elif bet_amount <= 0:
        await interaction.response.send_message("Nice Try")
        return
        
    try:
        choice = int(choice) 
        if choice > 36 or choice < 0:
            await interaction.response.send_message("Please choose a proper number in table (0 - 36)")
            return
    except ValueError:
        choice = choice.capitalize()
        if choice not in ["Red", "Black", "Odd", "Even", "Green"]:
            await interaction.response.send_message("Please choose either 'Black' or 'Red' or 'Green' or 'Odd' or 'Even' or a number between 0 and 36.")
            return

    roll = random.randint(0, 36)  # Numbers from 0 to 36
    parity = "Even" if roll != 0 and roll % 2 == 0 else "Odd"
    if roll in RED_NUMBERS:
        color = "Red"
    elif roll in BLACK_NUMBERS:
        color = "Black"
    elif roll == 0:
        color = "Green"

    winnings = 0
    if choice in ["Red", "Black"]:
        if choice == color:
            winnings = bet_amount * 2
    elif choice in ["Even", "Odd"]:
        if choice == parity:
            winnings = bet_amount * 2
    elif choice in ["Green"]:
        if choice == color:
            winnings = bet_amount * 36
    else:
        if choice == roll:
            winnings = bet_amount * 36

    # Update balance based on winnings or loss
    if winnings > 0:
        new_balance = user_balance + winnings - bet_amount
        await set_balance(interaction.user.id, new_balance)
        await interaction.response.send_message(
            f"The roulette landed on {roll} ({color}, {parity}).\n"
            f"You won ${winnings}! New balance: ${new_balance}."
        )
    else:
        new_balance = user_balance - bet_amount
        await set_balance(interaction.user.id, new_balance)
        await interaction.response.send_message(
            f"The roulette landed on {roll} ({color}, {parity}).\n"
            f"You lost ${bet_amount}. New balance: ${new_balance}."
        )


@client.tree.command(name="balance", description = "Get money in table")
async def balance(interaction: discord.Interaction):
    user_balance = await get_balance(interaction.user.id)
    if user_balance == 0:
        await set_balance(interaction.user.id, 100)
        await interaction.response.send_message(f"{interaction.user.name}, your broke reset balance to: ${100}")
    else:
        await interaction.response.send_message(f"{interaction.user.name}, your balance is: ${user_balance}")


@client.tree.command(name="help", description = "Get help")
async def help(interaction: discord.Interaction):
    help_text = (
            "```All Current ShayBot Commands:\n"
            "/help - Show this help message with a list of commands\n"
            "/balance - Check your current balance, set initial balance, and reset balance if you get to $0\n"
            "/coinflip <heads/tails> <amount> - Bet on a coinflip with the specified amount and choice\n"
            "/table - Display the balance of all users\n"
            "/roulette <black/red/green/odd/even/(number 0 - 36)> <amount>```\n"
        )
    await interaction.response.send_message(help_text)


@client.tree.command(name="table", description = "Table of users")
async def table(interaction: discord.Interaction):
    async with con.cursor() as cursor:
        await cursor.execute('SELECT id, money FROM users')
        rows = await cursor.fetchall()
        results = "\n".join([f"User: {interaction.guild.get_member(row[0]).name}, Balance: ${row[1]}" for row in rows])
        await interaction.response.send_message(results)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.id == 799084628324778025:  #medha
        await message.channel.send("Hi Medha :)")

    if message.author.id == 196113449099591681:  #me
        msg = message.content.split()
        if msg[0] == "++SetBalance":
            await set_balance(msg[1], msg[2])
            await message.channel.send("Done")

        



client.run(token)