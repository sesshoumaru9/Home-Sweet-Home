import re
from typing import Optional, List
import discord
from discord import app_commands
from discord.ext import commands
from hsh_bot.api import DiscordCommand, Command


@app_commands.describe(
    role_name="name of the color role (maximum 15 characters)",
    color_name="choose a generic color",
    color_hex="input a hexadecimal color code"
)
@app_commands.choices(
    color_name=[app_commands.Choice(name=c, value=c) for c in list(colors.keys())]
)
async def flair(self, interaction: discord.Interaction, role_name: app_commands.Range[str, 1, 15], color_name: Optional[str], color_hex: Optional[str]):
    if not interaction.guild:
        await interaction.response.send_message("you must run this command within a discord server.", ephemeral=True)
        return

    self.HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")
    role_name = f"✨ {role_name}"
    member = interaction.user

    if not isinstance(member, discord.Member):
        await interaction.response.send_message("you must run this command in a discord server.", ephemeral=True)
        return

    if color_name and color_hex:
        await interaction.response.send_message("you must choose either color name or color hex code, not both.", ephemeral=True)
        return

    if color_hex and not self.valid_hex_color(color_hex):
        await interaction.response.send_message("hex color is not in the format of `#ffffff` or `ffffff`.", ephemeral=True)
        return

    color = None
    if color_name:
        color = colors[color_name]
    elif color_hex:
        color_code = int(color_hex.lstrip('#'), 16)
        color = discord.Color(color_code)

    existing_roles = [r for r in interaction.guild.roles if r.name.startswith("✨")]
    color_match_role = None
    for role in existing_roles:
        if role.color == color:
            color_match_role = role
            break

    color_role = discord.utils.get(interaction.guild.roles, name=role_name)

    if color_role:
        if color and color_role.color == color:
            await interaction.response.send_message(f"assigning existing color role {role_name}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"a role named **{role_name}** already exists with a different color. please remove or rename it first.", ephemeral=True)
            return
    else:
        if not color:
            await interaction.response.send_message("please specify a color name or hex to create a new role.", ephemeral=True)
            return

        if color_match_role:
            color_role = color_match_role
            await interaction.response.send_message(f"reusing existing color role **{color_match_role.name}**.", ephemeral=True)
        else:
            color_role = await interaction.guild.create_role(
                name=role_name,
                color=color,
                permissions=discord.Permissions.none()
            )
            await color_role.edit(position=interaction.guild.me.top_role.position)
            await interaction.response.send_message(f"created new color role **{role_name}**.", ephemeral=True)

    for role in member.roles:
        if role.name.startswith("✨") and role != color_role:
            if len(role.members) == 1:
                await role.delete()
            else:
                await member.remove_roles(role)

    await member.add_roles(color_role)
    await interaction.followup.send(f"you now have the {role_name} flair!", ephemeral=True)
