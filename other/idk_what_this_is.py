import discord, os, asyncio
from discord import Bot
from dotenv import load_dotenv

load_dotenv(".env")
token = os.getenv("bot_token")
command_prefix = os.getenv("cmd_prefix")
intents = discord.Intents.all()

bot = discord.Bot(command_prefix=command_prefix, intents=intents, token=token)