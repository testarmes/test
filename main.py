import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True 

bot = commands.Bot(command_prefix="/", intents=intents)

STOCK_FILE = "stock.json"
message_id_global = None

def charger_stock():
    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_stock(stock):
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(stock, f, indent=4, ensure_ascii=False)

def generer_embed_stock():
    embed = discord.Embed(title="📦 Stock d'Armes", color=0x00ff00)
    for emoji, arme in stock_armes.items():
        if arme["disponible"]:
            statut = "✅ Disponible"
        else:
            user_mention = f"<@{arme['utilisateur']}>"
            statut = f"❌ Attribué à {user_mention}"
        embed.add_field(name=f"{emoji} {arme['nom']}",
                        value=statut,
                        inline=False)
    return embed

stock_armes = charger_stock()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

# ... (le reste de tes commandes ici, inchangé) ...

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    emoji = str(reaction.emoji)
    if emoji not in stock_armes:
        return

    arme = stock_armes[emoji]
    if not arme["disponible"]:
        await reaction.remove(user)
        return

    arme["disponible"] = False
    arme["utilisateur"] = user.id

    try:
        channel = reaction.message.channel
        message = await channel.fetch_message(message_id_global)
        await message.edit(embed=generer_embed_stock())
    except Exception as e:
        print(f"Erreur mise à jour message stock: {e}")

    sauvegarder_stock(stock_armes)

bot.run(os.getenv("DISCORD_TOKEN"))
