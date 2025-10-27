from typing import Optional
import discord
from hsh_bot.api import DiscordCommand, Command

class Hello(DiscordCommand):
    def user_commands(self):
        return [
            Command(
                name="hello",
                description="Says hi",
                callback=self.hello
            )
        ]

    async def hello(self, i: discord.Interaction, name: Optional[str]):
        if name:
            greeting = f"Hi, {name}"
        else:
            greeting = "Hi"

        await i.response.send_message(greeting, ephemeral=True)

