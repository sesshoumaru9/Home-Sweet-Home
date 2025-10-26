import asyncio

from hsh_bot.bot import discord_bot

# Import bot functionality
from . import bot
from .bot.discord_bot import bot as discord_bot

@discord_bot.event
async def on_ready():
    print(f"bot is online as {discord_bot.user}")


async def run_bot():
    await discord_bot.start("YOUR_BOT_TOKEN_HERE")

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
