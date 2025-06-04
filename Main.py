import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import json
import os
from dotenv import load_dotenv
load_dotenv()


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="GTR ", intents=intents, help_command=None)  # help_command=None deaktiviert den Standard-Help

SUPPORT_ROLE_NAME = "Support"  # fallback name, but overwritten by roles set
TICKET_CATEGORY_NAME = "Tickets"
SUPPORT_ROLES_FILE = "support_roles.json"

# Global list of support roles (discord.Role objects)
support_roles = []

def save_support_roles():
    # Save only role IDs to file
    with open(SUPPORT_ROLES_FILE, "w") as f:
        json.dump([role.id for role in support_roles], f)

def load_support_roles(guild):
    global support_roles
    support_roles.clear()
    if not os.path.isfile(SUPPORT_ROLES_FILE):
        return
    with open(SUPPORT_ROLES_FILE, "r") as f:
        try:
            role_ids = json.load(f)
        except json.JSONDecodeError:
            return
    for role_id in role_ids:
        role = guild.get_role(role_id)
        if role:
            support_roles.append(role)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    # Load support roles for all guilds, here only for first guild if you have just one server:
    for guild in bot.guilds:
        load_support_roles(guild)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Ping is: {latency} ms")

@bot.command()
async def bmw(ctx):
    await ctx.send(f"Benz > BMW")


@bot.command()
@commands.has_permissions(administrator=True)
async def set_support_roles(ctx):
    await ctx.send("Please mention all roles that should have support permissions. Send them as mentions separated by spaces.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=180.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond.")
        return

    roles = msg.role_mentions
    if not roles:
        await ctx.send("You did not mention any roles. Please try again.")
        return

    global support_roles
    support_roles = roles
    save_support_roles()

    role_names = ", ".join(role.name for role in roles)
    await ctx.send(f"Support roles have been set: {role_names}")

async def create_welcome_card(member):
    background = Image.open(r"C:\Users\azadk\Desktop\bot\Autobild.jpg").convert("RGBA")
    width, height = background.size

    avatar_asset = member.display_avatar.with_size(128).with_static_format('png')
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_asset.url) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((128, 128))

    mask = Image.new("L", (128, 128), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 128, 128), fill=255)
    avatar.putalpha(mask)

    avatar_pos = (50, height - 150)
    background.paste(avatar, avatar_pos, avatar)

    draw = ImageDraw.Draw(background)
    font_path = "arial.ttf"
    font = ImageFont.truetype(font_path, 40)

    text = f"Welcome,\n{member.name}!"
    text_pos = (avatar_pos[0] + 128 + 30, height - 150)

    shadowcolor = "black"
    x, y = text_pos
    draw.text((x-2, y-2), text, font=font, fill=shadowcolor)
    draw.text((x+2, y-2), text, font=font, fill=shadowcolor)
    draw.text((x-2, y+2), text, font=font, fill=shadowcolor)
    draw.text((x+2, y+2), text, font=font, fill=shadowcolor)
    draw.text(text_pos, text, font=font, fill="white")

    with io.BytesIO() as image_binary:
        background.save(image_binary, 'PNG')
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename="welcome_card.png")

@bot.event
async def on_member_join(member):
    channel_id = 1172955273896398918
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Welcome channel not found.")
        return

    file = await create_welcome_card(member)

    embed = discord.Embed(
        title="Welcome!",
        description=(
            "˚ ༘♡ ·˚꒰𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑡𝑜 𝑚𝑦 𝑠𝑒𝑟𝑣𝑒𝑟❦︎꒱ ₊˚ˑ༄\n"
            "+:ꔫ:﹤ღ﹥:ꔫ:+ﾟ\n"
            f".·:¨༺  {member.mention} ༻¨:·.\n"
            "السَلام عَلَيكم ورَحمَة اللهِ وَبَرَكاته\n"
            "𝑊𝑒'𝑟𝑒 𝑔𝑙𝑎𝑑 𝑦𝑜𝑢'𝑟𝑒 ℎ𝑒𝑟𝑒. 𝐻𝑎𝑣𝑒 𝑓𝑢𝑛 𝑎𝑛𝑑 𝑓𝑒𝑒𝑙 𝑎𝑡 ℎ𝑜𝑚𝑒 <:emoji_9:1172593828948090901>\n\n"
            "𝐹𝑒𝑒𝑙 𝑓𝑟𝑒𝑒 𝑡𝑜 𝑐ℎ𝑒𝑐𝑘 𝑜𝑢𝑡 𝑡ℎ𝑒 𝑜𝑡ℎ𝑒𝑟 𝑐ℎ𝑎𝑛𝑛𝑒𝑙𝑠 \n\n"
            "✧-┊𝐑𝐮𝐥𝐞𝐬 → <#1172955291768324146>\n"
            "✧-┊𝐒𝐞𝐥𝐟𝐫𝐨𝐥𝐞𝐬 → <#1172955304745513090>\n"
            "✰-┊𝐂𝐡𝐚𝐭 → <#1177675040066654239>"
        ),
        color=0x0B0B6D
    )
    embed.set_image(url="attachment://welcome_card.png")

    await channel.send(embed=embed, file=file)

@bot.command()
async def setup_ticket(ctx):
    file = discord.File(r"C:\Users\azadk\Desktop\Bot\ticket.jpg", filename="ticket.jpg")

    embed = discord.Embed(
        title="Support Ticket",
        description="Click 🎫 to open a ticket.",
        color=0x0B0B6D
    )
    embed.set_image(url="attachment://ticket.jpg")

    message = await ctx.send(embed=embed, file=file)
    await message.add_reaction("🎫")
    await message.pin()

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != "🎫":
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member.bot:
        return

    category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
    if category is None:
        # Instead of creating category, abort or create manually
        await member.send(f"The ticket category `{TICKET_CATEGORY_NAME}` was not found. Please contact an admin.")
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    # Add support roles permissions
    for role in support_roles:
        guild_role = get(guild.roles, id=role.id)
        if guild_role:
            overwrites[guild_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    channel_name = f"ticket-{member.name}".lower().replace(" ", "-")
    existing = discord.utils.get(guild.text_channels, name=channel_name)
    if existing:
        try:
            await member.send("You already have an open ticket.")
        except discord.Forbidden:
            pass
        return

    ticket_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
    await ticket_channel.send(f"{member.mention}, welcome to the support ticket! Close the ticket with `GTR close`.")

    # Ping support roles
    support_roles_mentions = " ".join(role.mention for role in support_roles if get(guild.roles, id=role.id))
    if support_roles_mentions:
        await ticket_channel.send(f"{support_roles_mentions} — A new ticket has been opened!")

@bot.command()
async def close(ctx):
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("You can only use this command inside a ticket channel.")
        return

    # Prüfen, ob der Benutzer eine der Supportrollen hat
    if not any(role.id in [sr.id for sr in support_roles] for role in ctx.author.roles):
        await ctx.send("You don't have permission to close this ticket.")
        return

    await ctx.channel.delete()

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="Help Center",
        description="Here are all available commands:",
        color=0x0B0B6D
    )
    embed.add_field(name="GTR help", value="Shows this help message.", inline=False)
    embed.add_field(name="GTR ping", value="Shows the bot's latency.", inline=False)
    embed.add_field(name="GTR setup_ticket", value="Creates the ticket embed with reaction.", inline=False)
    embed.add_field(name="🎫 (reaction)", value="Opens a support ticket.", inline=False)
    embed.add_field(name="GTR close", value="Closes an open ticket (only inside ticket channel).", inline=False)
    await ctx.send(embed=embed)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(DISCORD_TOKEN)