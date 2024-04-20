import discord
from discord.ext import commands
from discord import Embed, ButtonStyle
from discord.ext import commands
from discord.ui import View, Button
import math

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

intents = discord.Intents.all()
intents.message_content = True

# Initialize the Bot with intents
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
    async def prev_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % ((len(self.items) - 1) // 5 + 1)
        await self.show_page()

    @discord.ui.button(label="🔽", style=discord.ButtonStyle.blurple)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = (self.current_page + 1) % ((len(self.items) - 1) // 5 + 1)
        await self.show_page()

def create_embed(page, items):
    items_per_page = 5
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
    async def decrease(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.quantity > 1:
            self.quantity -= 1
            await interaction.response.edit_message(embed=self.create_embed())

    @discord.ui.button(label="+", style=discord.ButtonStyle.green)
    async def increase(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.quantity < 10:  # Set a maximum quantity (adjust as needed)
            self.quantity += 1
            await interaction.response.edit_message(embed=self.create_embed())

    def create_embed(self):
        embed = Embed(title=f"Purchase {self.item_name}", description=f"Quantity: {self.quantity}")
        return embed

class ConfirmationButtons(discord.ui.View):
    def __init__(self, item_name, quantity):
        super().__init__()
        self.item_name = item_name
        self.quantity = quantity

    @discord.ui.button(label="Confirm", style=ButtonStyle.green)
    async def confirm(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.create_embed(), view=None)

    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel(self, button: Button, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=Embed(description="Purchase canceled."), view=None)

    def create_embed(self):
        total_price = items[self.item_name] * self.quantity
        embed = Embed(title="Purchase Confirmation", description=f"Item: {self.item_name}\nQuantity: {self.quantity}\nTotal Price: {total_price} credits")
        return embed

@bot.command()
async def buy(ctx, item_number: int = None):
    print(f"Debug: item_number = {item_number}")
    # Check if the selected item number is within the valid range

        selected_item = list(items.keys())[item_number - 1]

        # Create and send the quantity selection view
        quantity_view = QuantityButtons(selected_item)
        quantity_message = await ctx.send(embed=quantity_view.create_embed(), view=quantity_view)

        # Wait for the user to select a quantity
        try:
            interaction = await bot.wait_for(
                "button_click",
                check=lambda i: i.custom_id in ("increase", "decrease"),
                timeout=30.0,
            )
            await interaction.response.defer()
        except TimeoutError:
            await ctx.send("Purchase canceled due to inactivity.")
            return

        # Create and send the confirmation view
        confirmation_view = ConfirmationButtons(selected_item, quantity_view.quantity)
        confirmation_message = await ctx.send(embed=confirmation_view.create_embed(), view=confirmation_view)

        # Wait for the user to confirm or cancel the purchase
        try:
            interaction = await bot.wait_for(
                "button_click",
                check=lambda i: i.custom_id in ("confirm", "cancel"),
                timeout=30.0,
            )
            await interaction.response.defer()
        except TimeoutError:
            await ctx.send("Purchase canceled due to inactivity.")
            return

        if interaction.custom_id == "confirm":
            # Perform the purchase and send a confirmation message
            total_price = items[selected_item] * quantity_view.quantity
            await ctx.send(f"You purchased {quantity_view.quantity} {selected_item}(s) for {total_price} credits! The trader will deliver it soon.")




@bot.command()
async def help(ctx):
    embed = Embed(title="Available Commands", description="List of available commands:")
    embed.add_field(name="!buy", value="- Buy a product", inline=False)
    embed.add_field(name="!show", value="- Show items available to purchase", inline=False)
    embed.add_field(name="!help", value="- Show this help message", inline=False)
    await ctx.send(embed=embed)



bot.run(Token)
