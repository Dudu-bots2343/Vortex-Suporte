import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# ===================== CONFIG =====================
TOKEN = os.getenv("TOKEN")  # Token no Render
STAFF_ROLE_NAME = "Staff"
CATEGORY_NAME = "Tickets"
TICKET_CHANNEL_ID = 123456789012345678  # ID do canal fixo
# ==================================================

# ===================== BOT =====================
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===================== FLASK (UPTIME) =====================
app = Flask("")

@app.route("/")
def home():
    return "Bot Discord online 24/7!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()

# ===================== FECHAR TICKET =====================
class FecharTicket(discord.ui.View):
    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.secondary)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

# ===================== CRIAR TICKET =====================
async def criar_ticket(interaction, tipo, emoji):
    guild = interaction.guild
    user = interaction.user

    staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)

    if category is None:
        category = await guild.create_category(CATEGORY_NAME)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    channel = await guild.create_text_channel(
        name=f"{tipo}-{user.name}",
        category=category,
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"{emoji} Ticket de {tipo.capitalize()}",
        description="Descreva o assunto com detalhes.",
        color=discord.Color.blue()
    )

    await channel.send(content=user.mention, embed=embed, view=FecharTicket())
    await interaction.response.send_message(
        f"✅ Ticket criado: {channel.mention}",
        ephemeral=True
    )

# ===================== PAINEL =====================
class TicketView(discord.ui.View):
    @discord.ui.button(label="🚨 Denúncia", style=discord.ButtonStyle.danger)
    async def denuncia(self, interaction: discord.Interaction, button: discord.ui.Button):
        await criar_ticket(interaction, "denuncia", "🚨")

    @discord.ui.button(label="❓ Dúvida", style=discord.ButtonStyle.primary)
    async def duvida(self, interaction: discord.Interaction, button: discord.ui.Button):
        await criar_ticket(interaction, "duvida", "❓")

    @discord.ui.button(label="💡 Sugestão", style=discord.ButtonStyle.success)
    async def sugestao(self, interaction: discord.Interaction, button: discord.ui.Button):
        await criar_ticket(interaction, "sugestao", "💡")

# ===================== BOT READY =====================
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    channel = bot.get_channel(TICKET_CHANNEL_ID)
    if not channel:
        print("Canal de ticket não encontrado.")
        return

    async for msg in channel.history(limit=10):
        if msg.author == bot.user:
            return

    embed = discord.Embed(
        title="🎫 Central de Atendimento",
        description=(
            "Escolha uma opção abaixo:\n\n"
            "🚨 Denúncias\n"
            "❓ Dúvidas\n"
            "💡 Sugestões"
        ),
        color=discord.Color.green()
    )

    await channel.send(embed=embed, view=TicketView())

# ===================== START =====================
keep_alive()
bot.run(TOKEN)
