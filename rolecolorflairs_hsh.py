import discord
from discord.ext import commands

# --- setup ---
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- color options dictionary (easy to edit later) ---
colors = {
    "red": "❤️",
    "orange": "🧡",
    "yellow": "💛",
    "green": "💚",
    "blue": "💙",
    "purple": "💜",
    "pink": "🌸",
    "white": "🤍",
    "black": "🖤",
}


@bot.event
async def on_ready():
    print(f"bot is online as {bot.user}")


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


# ---------- FLAIR COMMAND ----------

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)  # 1 use / 30 seconds per user
async def flair(ctx: commands.Context, *, title_and_color: str = None):
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


# ---------- REMOVE FLAIR ----------

@bot.command()
async def removeflair(ctx: commands.Context):
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


# ---------- LIST FLAIRS ----------

@bot.command()
async def listflairs(ctx: commands.Context):
    flairs = [r.name for r in ctx.guild.roles if r.name.startswith("✨")]
    if flairs:
        await ctx.send("✨ current flairs:\n" + "\n".join(flairs))
    else:
        await ctx.send("no flairs exist yet")


# ---------- COOLDOWN ERROR HANDLER ----------

@flair.error
async def flair_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"wait {error.retry_after:.1f}s before using this again!")
    else:
        raise error


# ---------- RUN ----------
bot.run("YOUR_BOT_TOKEN_HERE")

