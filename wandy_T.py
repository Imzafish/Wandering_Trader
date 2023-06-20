import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')

@bot.command(
    name="buy",
    description="Buy a product"
)
async def buy(ctx, product: str, quantity: int):
    await ctx.send(f"You want to buy {quantity} {product}(s).")
    receipts_channel = discord.utils.get(ctx.guild.channels, name="receipts")
    if receipts_channel:
        await receipts_channel.send(f"Purchase confirmation: You bought {quantity} {product}(s).")
    else:
        await ctx.send(f"Purchase confirmation: You bought {quantity} {product}(s).")

@bot.command(
    name="trade",
    description="Ping traders"
)
async def trade(ctx):
    traders_role = discord.utils.get(ctx.guild.roles, name="Trader")
    if traders_role:
        await ctx.send(f"{traders_role.mention}, someone is requesting assistance!")
    else:
        await ctx.send("No traders role found.")

@bot.command(
    name="add_item",
    description="Add an item to the buy list"
)
async def add_item(ctx, *, item: str):
    buy_list_channel = discord.utils.get(ctx.guild.channels, name="buy-list")
    if buy_list_channel:
        await buy_list_channel.send(f"New item added to the buy list: {item}.")
        await ctx.send(f"Item '{item}' added to the buy list.")
    else:
        await ctx.send("Error: Buy list channel not found.")

@bot.command(
    name="open_thread",
    description="Open a private thread"
)
async def open_thread(ctx):
    user = ctx.author
    guild = ctx.guild
    
    existing_thread = discord.utils.get(guild.threads, name=f"Private Thread with {user.name}")
    
    if existing_thread:
        await ctx.send(f"A private thread with {user.mention} already exists: {existing_thread.mention}")
    else:
        category = discord.utils.get(guild.categories, name="Private Threads")
        if category is None:
            category = await guild.create_category("Private Threads")
        thread = await category.create_text_channel(f"private-thread-{user.name}")
        await thread.send(f"This is a private thread between {user.mention} and traders.")
        await thread.send("Traders, please assist in this thread.")

@bot.command(
    name="help",
    description="Recap all features"
)
async def help_command(ctx):
    help_message = """Available Commands:
    /buy <product> <quantity> - Buy a product
    /trade - Ping traders
    /add_item <item> - Add an item to the buy list
    /open_thread - Open a private thread
    /help - Show this help message"""
    await ctx.send(help_message)

bot.run('YOUR_BOT_TOKEN')
