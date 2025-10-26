import discord
from discord import app_commands

# --- setup ---
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

class DiscordBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

bot = DiscordBot()
