import asyncio
import discord
from discord.ext import commands
import os

import utils.db as db
from utils.gspread import setup_gspread

from dotenv import load_dotenv
load_dotenv()

class FalconBot(commands.Bot):
    async def setup_hook(self):
        await db.init()
        self.gspread = setup_gspread()
        await self.load_extension("extensions.attendance")
        # await self.tree.sync()

    async def close(self):
        await db.close()
        await super().close()

    async def on_ready(self):
        print(f"Logged in as {self.user}!")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = FalconBot(command_prefix="/", help_command=None, intents=intents)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

async def main():
    async with bot:
        await bot.start(DISCORD_BOT_TOKEN)

asyncio.run(main())