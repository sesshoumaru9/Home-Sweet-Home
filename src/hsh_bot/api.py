from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Callable, Awaitable, Any
from .bot.discord_bot import bot

@dataclass
class Command:
    name: str
    description: str
    callback: Callable[..., Awaitable]

class DiscordCommand(ABC):
    registered_commands = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        commands = cls().user_commands()
        for command in commands:
            if command.name in cls.registered_commands:
                raise KeyError(f"{command.name} is already a registered command")

            cls.registered_commands[command.name] = command
            bot.tree.command(name=command.name, description=command.description)(command.callback)


    @abstractmethod
    def user_commands(self) -> List[Command]: pass
