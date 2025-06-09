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
        try:
            with open(STOCK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Fichier vide ou corrompu -> on retourne un dict vide
            return {}
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


@bot.command()
async def stock(ctx):
    global message_id_global
    message = await ctx.send(embed=generer_embed_stock())
    message_id_global = message.id
    for emoji in stock_armes:
        try:
            await message.add_reaction(emoji)
        except:
            pass 
    sauvegarder_stock(stock_armes)


@bot.command()
async def rend(ctx, emoji: str):
    if emoji not in stock_armes:
        await ctx.send(f"❌ L'arme {emoji} n'existe pas.")
        return

    arme = stock_armes[emoji]
    if arme["utilisateur"] == ctx.author.id:
        arme["disponible"] = True
        arme["utilisateur"] = None
        await ctx.send(f"✅ Tu as rendu l'arme {emoji} ({arme['nom']})")

      
        try:
            channel = ctx.channel
            message = await channel.fetch_message(message_id_global)
            await message.edit(embed=generer_embed_stock())
        except Exception as e:
            print(f"Erreur mise à jour message stock: {e}")

        sauvegarder_stock(stock_armes)
    else:
        await ctx.send("❌ Tu ne possèdes pas cette arme.")


@bot.command()
async def ajouterarme(ctx, emoji: str, *, nom: str):
    if emoji in stock_armes:
        await ctx.send("❌ Cette arme existe déjà.")
        return

    stock_armes[emoji] = {"nom": nom, "disponible": True, "utilisateur": None}

    await ctx.send(f"✅ Arme ajoutée : {emoji} **{nom}**")

    try:
        channel = ctx.channel
        message = await channel.fetch_message(message_id_global)
        await message.edit(embed=generer_embed_stock())
        await message.add_reaction(emoji)
    except Exception as e:
        print(f"Erreur mise à jour message stock ou ajout réaction: {e}")

    sauvegarder_stock(stock_armes)


@bot.command(name="supprimearme")
async def supprimer_arme(ctx, emoji: str):
    global stock_armes
    if emoji in stock_armes:
        nom = stock_armes[emoji]["nom"]
        del stock_armes[emoji]
        sauvegarder_stock(stock_armes)
        await ctx.send(f"🗑️ Arme {emoji} ({nom}) supprimée du stock.")

        try:
            message = await ctx.channel.fetch_message(message_id_global)
            await message.edit(embed=generer_embed_stock())

      
            for reaction in message.reactions:
                if str(reaction.emoji) == emoji:
                    await message.clear_reaction(emoji)
                    break
        except Exception as e:
            print(f"Erreur mise à jour message stock ou suppression réaction: {e}")
    else:
        await ctx.send(f"❌ Aucune arme associée à {emoji}.")


@bot.command()
async def resetstock(ctx):
    for arme in stock_armes.values():
        arme["disponible"] = True
        arme["utilisateur"] = None
    await ctx.send("♻️ Le stock a été réinitialisé.")
    try:
        channel = ctx.channel
        message = await channel.fetch_message(message_id_global)
        await message.edit(embed=generer_embed_stock())
    except Exception as e:
        print(f"Erreur mise à jour message stock: {e}")
    sauvegarder_stock(stock_armes)


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
