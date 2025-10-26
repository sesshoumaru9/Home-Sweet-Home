from typing import Union
import discord
from discord.ext import commands
from hsh_bot.api import DiscordCommand, Command

class Flair(DiscordCommand):
# --- color options dictionary (easy to edit later) ---
    colors = {
        "Red": "❤️",
        "Orange": "🧡",
        "Yellow": "💛",
        "Green": "💚",
        "Blue": "💙",
        "Purple": "💜",
        "Pink": "🌸",
        "White": "🤍",
        "Black": "🖤",
    }

    def user_commands(self):
        return [
            Command(
                "flair",
                "Change your username color and role",
                self.flair
            ),
            Command(
                "remove-flair",
                "Remove your current username color and role",
                self.removeflair
            ),
            Command(
                "list-flairs",
                "List the current flairs in the server",
                self.listflairs
            )
        ]

    async def flair(self, ctx: commands.Context, *, title_and_color: Union[str, None] = None):
        """
        Examples:
        !flair drifting soul
        !flair drifting soul | #ff66cc
        """
        member = ctx.author
        # user used hex code
        if title_and_color and "|" in title_and_color:
            title, color_text = [x.strip() for x in title_and_color.split("|", 1)]

            if not color_text.startswith("#") or len(color_text) not in (4, 7):
                return await ctx.send("please use a valid hex color (like #ff66cc)")

            try:
                hex_value = int(color_text[1:], 16)
                color = discord.Color(hex_value)
            except ValueError:
                return await ctx.send("couldn't read that color code")

            # remove their old flair if it exists
            for role in member.roles:
                if role.name.startswith("✨"):
                    member_count = sum(1 for m in ctx.guild.members if role in m.roles)
                    await member.remove_roles(role)
                    if member_count <= 1:
                        try:
                            await role.delete()
                        except discord.Forbidden:
                            pass

            new_role = await ctx.guild.create_role(
                name=f"✨ {title}",
                color=color,
                permissions=discord.Permissions.none(),
            )
            await member.add_roles(new_role)
            return await ctx.send(f"✨ created **{title}** with color {color_text}!")

        # no hex → open dropdown
        if title_and_color:
            title = title_and_color.strip()
        else:
            return await ctx.send("use `!flair title` or `!flair title | #hexcolor`")

        view = ColorSelectView(title)
        await ctx.send(f"choose a color for **{title}**", view=view)

    async def removeflair(self, ctx: commands.Context):
        member = ctx.author
        removed = False
        for role in member.roles:
            if role.name.startswith("✨"):
                member_count = sum(1 for m in ctx.guild.members if role in m.roles)
                await member.remove_roles(role)
                if member_count <= 1:
                    try:
                        await role.delete()
                    except discord.Forbidden:
                        pass
                removed = True
        if removed:
            await ctx.send("your flair was removed")
        else:
            await ctx.send("you don't have one")

    async def listflairs(self, ctx: commands.Context):
        flairs = [r.name for r in ctx.guild.roles if r.name.startswith("✨")]
        if flairs:
            await ctx.send("✨ current flairs:\n" + "\n".join(flairs))
        else:
            await ctx.send("no flairs exist yet")


# ---------- COLOR SELECT DROPDOWN ----------

class ColorSelect(discord.ui.Select):
    def __init__(self, title: str):
        # Build options dynamically from the colors dictionary
        options = [
            discord.SelectOption(label=color, emoji=emoji)
            for color, emoji in colors.items()
        ]
        super().__init__(placeholder="pick a color", options=options)
        self.title = title

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild

        # Remove and clean up old flair roles
        for role in member.roles:
            if role.name.startswith("✨"):
                member_count = sum(1 for m in guild.members if role in m.roles)
                await member.remove_roles(role)
                if member_count <= 1:
                    try:
                        await role.delete()
                    except discord.Forbidden:
                        pass

        color_name = self.values[0].lower()
        color = getattr(discord.Color, color_name)()

        new_role = await guild.create_role(
            name=f"✨ {self.title}",
            color=color,
            permissions=discord.Permissions.none(),
        )
        await member.add_roles(new_role)

        await interaction.response.edit_message(
            content=f"✨ you now have **{self.title}** in {color_name}!", view=None
        )


class ColorSelectView(discord.ui.View):
    def __init__(self, title: str):
        super().__init__()
        self.add_item(ColorSelect(title))

