import discord
from discord.ext import commands
from discord import Embed, ButtonStyle
from discord.ui import View, Button
import math
import os
from keep_alive import keep_alive
keep_alive()

items = {
    "Product 1": 10,
    "Product 2": 15,
    "Product 3": 20,
    "Product 4": 25,
    "Product 5": 30,
    "Product 6": 35,
    "Product 7": 40,
    "Product 8": 45,
    "Product 9": 50,
    "Product 10": 55,
}

ITEMS_PER_PAGE = 5
MAX_QUANTITY = 10
MIN_QUANTITY = 1

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to the discord server")

class Buttons(discord.ui.View):
    def __init__(self, ctx, items, timeout=180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.items = items
        self.current_page = 0
        self.message = None

    async def show_page(self):
        embed = create_embed(self.current_page, self.items)
        if not self.message:
            self.message = await self.ctx.send(embed=embed, view=self)
        else:
            await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="🔼", style=discord.ButtonStyle.blurple)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % ((len(self.items) - 1) // ITEMS_PER_PAGE + 1)
        await interaction.response.edit_message(embed=create_embed(self.current_page, self.items), view=self)

    @discord.ui.button(label="🔽", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % ((len(self.items) - 1) // ITEMS_PER_PAGE + 1)
        await interaction.response.edit_message(embed=create_embed(self.current_page, self.items), view=self)

def create_embed(page, items):
    items_per_page = ITEMS_PER_PAGE
    total_pages = math.ceil(len(items) / items_per_page)

    start_index = page * items_per_page
    end_index = (page + 1) * items_per_page

    embed = Embed(title=f"List of Items (Page {page + 1}/{total_pages})", description="Type the number of the item you wish to purchase.")
    for i, (item, price) in enumerate(list(items.items())[start_index:end_index], start=start_index + 1):
        embed.add_field(name=f"{i}. {item}", value=f"Price: {price}", inline=False)

    return embed

@bot.command()
async def show(ctx):
    view = Buttons(ctx, items)
    await view.show_page()

class QuantityButtons(discord.ui.View):
    def __init__(self, item_name):
        super().__init__()
        self.item_name = item_name
        self.quantity = 1

    @discord.ui.button(label="-", style=discord.ButtonStyle.red)
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.quantity > MIN_QUANTITY:
            self.quantity -= 1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="+", style=discord.ButtonStyle.green)
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.quantity < MAX_QUANTITY:
            self.quantity += 1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Next", style=ButtonStyle.blurple)
    async def next_step(self, interaction: discord.Interaction, button: Button):
        view = ConfirmationButtons(self.item_name, self.quantity)
        await interaction.response.edit_message(embed=view.create_embed(), view=view)

    def create_embed(self):
        embed = Embed(title=f"Purchase {self.item_name}", description=f"Quantity: {self.quantity}")
        return embed

class ConfirmationButtons(discord.ui.View):
    def __init__(self, item_name, quantity):
        super().__init__()
        self.item_name = item_name
        self.quantity = quantity

    @discord.ui.button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        total_price = items[self.item_name] * self.quantity
        await interaction.response.edit_message(
            content=f"You purchased {self.quantity} {self.item_name}(s) for {total_price} credits!",
            embed=None,
            view=None
        )

    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=Embed(description="Purchase canceled."), view=None)

    def create_embed(self):
        total_price = items[self.item_name] * self.quantity
        embed = Embed(title="Purchase Confirmation", description=f"Item: {self.item_name}\nQuantity: {self.quantity}\nTotal Price: {total_price} credits")
        return embed

@bot.command()
async def buy(ctx, item_number: int = None):
    if item_number is None or item_number < 1 or item_number > len(items):
        await ctx.send("Please enter a valid item number.")
        return

    selected_item = list(items.keys())[item_number - 1]
    view = QuantityButtons(selected_item)
    await ctx.send(embed=view.create_embed(), view=view)

@bot.command()
async def help(ctx):
    embed = Embed(title="Available Commands", description="List of available commands:")
    embed.add_field(name="!buy <item_number>", value="- Buy a product", inline=False)
    embed.add_field(name="!show", value="- Show items available to purchase", inline=False)
    embed.add_field(name="!help", value="- Show this help message", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))

