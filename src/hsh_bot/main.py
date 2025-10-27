import asyncio
import os
import signal
from dotenv import load_dotenv

# Load .env if it exists
load_dotenv()

BOT_TOKEN = os.getenv("HSH_BOT_TOKEN", "")

from hsh_bot.bot import discord_bot

# Import bot functionality
from . import bot
from .bot.discord_bot import bot as discord_bot

async def run_bot():
    # Event that shutdowns the server
    stop_event = asyncio.Event()

    def stop_server():
        print("Stopping the server...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_server)

    # Start the bot
    bot_task = asyncio.create_task(discord_bot.start(BOT_TOKEN))

    # Wait for signal
    await stop_event.wait()

    # Close the bot
    await discord_bot.close()

    # Wait for the bot task to end
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


def main():
    print("Running bot...")
    print("Using Token:", BOT_TOKEN)
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
