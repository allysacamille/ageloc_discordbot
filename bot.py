import os
import discord
from discord import app_commands
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("MTM1OTg4MDkxMjM0MjQ4Mjk2NA.G7abk4.1BQrZG_8rqqVAa8dWOy6x0IBGhemoSk5TDXPN4")
MONGO_URI = os.getenv("mongodb://allysacamille:<db_password>@ac-vyrjfnz-shard-00-00.ayzdutt.mongodb.net:27017,ac-vyrjfnz-shard-00-01.ayzdutt.mongodb.net:27017,ac-vyrjfnz-shard-00-02.ayzdutt.mongodb.net:27017/?replicaSet=atlas-y7lk1m-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster1")

# Setup MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["discord_bot"]
user_collection = db["users"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}.")

@bot.tree.command(name="start", description="Begin setup")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message("What's your age?", ephemeral=True)

    def check_age(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        age_msg = await bot.wait_for("message", check=check_age, timeout=60)
        age = age_msg.content

        await interaction.followup.send("Where are you from?", ephemeral=True)

        def check_location(m):
            return m.author == interaction.user and m.channel == interaction.channel

        location_msg = await bot.wait_for("message", check=check_location, timeout=60)
        location = location_msg.content

        await user_collection.insert_one({
            "user_id": interaction.user.id,
            "username": interaction.user.name,
            "age": age,
            "location": location
        })

        await interaction.followup.send("✅ Info saved! Thank you!", ephemeral=True)

    except Exception as e:
        await interaction.followup.send("⏰ Timed out or an error occurred.", ephemeral=True)
        print(f"Error: {e}")

bot.run(DISCORD_TOKEN)
