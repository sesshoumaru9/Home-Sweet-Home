from abc import ABC
from dataclasses import dataclass
from typing import List, Callable
from discord.app_commands import Command
from .bot.discord_bot import bot


class DiscordCommand(ABC):
    registered_commands = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        commands = cls().user_commands()
        for command in commands:
            if command.name in cls.registered_commands:
                raise KeyError(f"{command.name} is already a registered command")

            cls.registered_commands[command.name] = command
            bot.tree.add_command(command)


    def user_commands(self) -> List[Command]: return []
