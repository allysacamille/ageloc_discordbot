import os
import discord
from discord import app_commands
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Setup MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["discord_bot"]
user_collection = db["users"]

# Enable necessary intents for your bot (e.g., member updates, presence updates)
intents = discord.Intents.default()
intents.message_content = True  # Allow bot to read message content
intents.members = True  # Enable member updates (e.g., when members join/leave)
intents.presences = True  # Enable presence updates (e.g., tracking online status)

# Create bot instance with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Setup Flask app to bind to a port
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Run the bot when it's ready
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

# Run Flask app in the background
def keep_alive():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# Run both Flask and Discord bot
if __name__ == "__main__":
    t = Thread(target=keep_alive)
    t.start()
    bot.run(DISCORD_TOKEN)
