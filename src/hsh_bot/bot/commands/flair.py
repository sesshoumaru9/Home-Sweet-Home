import re
from typing import Optional, List
import discord
from discord import app_commands
from discord.ext import commands
from hsh_bot.api import DiscordCommand, Command


# --- color options dictionary (easy to edit later) ---
# This needs to be global for the choices to work
colors = {
    "red": discord.Color.red(),
    "orange": discord.Color.orange(),
    "yellow": discord.Color.yellow(),
    "green": discord.Color.green(),
    "blue": discord.Color.blue(),
    "purple": discord.Color.purple(),
    "pink": discord.Color.pink(),
    "teal": discord.Color.teal(),
    "gold": discord.Color.gold(),
    "magenta": discord.Color.magenta(),
}

class Flair(DiscordCommand):
    HEX_COLOR_RE = re.compile(r"^#?[1-9a-fA-F]{6}$")

    def valid_hex_color(self, hex: str) -> bool:
        return bool(self.HEX_COLOR_RE.fullmatch(hex))

    def user_commands(self):
        return [
            Command(
                name="flair-set",
                description="Change your username color and role",
                callback=self.flair
            ),
            Command(
                name="flair-remove",
                description="Remove your current username color and role",
                callback=self.removeflair
            ),
            Command(
                name="flair-list",
                description="List the current flairs in the server",
                callback=self.listflairs
            )
        ]

    @app_commands.describe(
        role_name="Name of the color role (maximum 15 characters)",
        color_name="Choose a generic color",
        color_hex="Input a hexadecimal color code"
    )
    @app_commands.choices(
        color_name=[app_commands.Choice(name=c, value=c) for c in list(colors.keys())]
    )
    async def flair(self, interaction: discord.Interaction, role_name: app_commands.Range[str, 1, 15], color_name: Optional[str], color_hex: Optional[str]):
        """
        Examples:
        /flair drifting soul red
        /flair drifting soul #ff66cc
        """
        if not interaction.guild:
            await interaction.response.send_message("You must run this command within a discord server", ephemeral=True)
            return

        role_name = f"✨ {role_name}"
        color_role = discord.utils.get(interaction.guild.roles, name=role_name)

        if color_role and (color_name or color_hex):
            await interaction.response.send_message("Do not specify a color name or color hex code for roles that already exist", ephemeral=True)
            return

        if not color_name and not color_hex and not color_role:
            await interaction.response.send_message("Existing color role not found.", ephemeral=True)
            return

        if color_name and color_hex:
            await interaction.response.send_message("You must choose either color name or color hex code, not both", ephemeral=True)
            return

        if color_hex and not self.valid_hex_color(color_hex):
            await interaction.response.send_message("Hex color is not in the format of `#FFFFFF` or `FFFFFF`", ephemeral=True)
            return

        member = interaction.user
        if not member or not isinstance(member, discord.Member):
            return

        color = None
        if color_name:
            # user used named color
            color = colors[color_name]

        if color_hex:
            color_code = int(color_hex.lstrip('#'), 16)
            color = discord.Color(color_code)

        if not color_role:
            if not color:
                await interaction.response.send_message("Failed to create the specified color", ephemeral=True)
                return

            color_role = await interaction.guild.create_role(
                name=role_name,
                color=color,
                permissions=discord.Permissions.none(),
            )

            await color_role.edit(position=interaction.guild.me.top_role.position)

        await interaction.response.send_message("Assigning you to your new color role", ephemeral=True)

        for role in member.roles:
            if role.name.startswith("✨"):
                if len(role.members) == 1:
                    await role.delete()
                else:
                    await member.remove_roles(role)

        await member.add_roles(color_role)

    async def removeflair(self, interaction: discord.Interaction):
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message("You must run this command in a discord server", ephemeral=True)
            return

        await interaction.response.send_message("Attempting to remove your current color role...", ephemeral=True)

        removed = False
        for role in member.roles:
            if role.name.startswith("✨"):
                if len(role.members) == 1:
                    await role.delete()
                else:
                    await member.remove_roles(role)

                removed = True

        if removed:
            await interaction.followup.send("Your color role has been removed.", ephemeral=True)
        else:
            await interaction.followup.send("You currently do not have a color role.", ephemeral=True)

    async def listflairs(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        await interaction.response.send_message("Generating flair list...", ephemeral=True)

        flair_roles = [r for r in interaction.guild.roles if r.name.startswith("✨")]
        if not flair_roles:
            await interaction.followup.send("No color flairs exist yet.", ephemeral=True)
            return

        embeds = []
        for role in flair_roles:
            color = role.color
            name = role.name.lstrip("✨ ")
            embed = discord.Embed(
                description=name,
                color=color
            )
            embeds.append(embed)

        await interaction.followup.send(embeds=embeds, ephemeral=True)
