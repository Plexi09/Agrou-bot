from dotenv import load_dotenv
import logging
import os
import random
from interactions import (
    listen,
    slash_command,
    SlashContext,
    OptionType,
    slash_option,
    Intents,
    Client,
    ButtonStyle,
    Button
)

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

# Configuration du bot et des intents
intents = Intents.ALL
bot = Client(token=BOT_TOKEN, intents=intents)

# Fonction appelée lorsque le bot est prêt
@listen()
async def on_ready():
    logger.info(f'Connecté en tant que {bot.user}')

# Commande pour démarrer une partie de Loups Garous
@slash_command(name="warewolf", description="Démarre une partie de Loups Garous avec les membres de votre salon vocal.")
@slash_option(name="joueurs", description="Nombre de joueurs", opt_type=OptionType.INTEGER, required=True)
@slash_option(name="loups", description="Proportion de loup en %", opt_type=OptionType.INTEGER, required=False)
@slash_option(name="force", description="Force le démarrage de la partie", opt_type=OptionType.BOOLEAN, required=False)
async def warewolf_function(ctx: SlashContext, joueurs: int, loups: int = 30, force: bool = False):
    logger.info(f'Commande /warewolf appelée par {ctx.author.display_name} avec {joueurs} joueurs et {loups}% loups.')
    
    # Si la partie est forcée
    if force:
        logger.info("Démarrage de la partie forcé !")
        await ctx.send("🚨 Démarrage de la partie forcé ! Attendez-vous à des erreurs si les conditions de partie ne sont pas atteintes. 🚨")
        await start_game(ctx, joueurs, loups, force)
        return

    # Si la partie n'est pas forcée
    if not force:
        # Vérifie les conditions de démarrage
        if joueurs < 5:
            logger.warning(f"Le nombre de joueurs doit être supérieur ou égal à 5 ! Vous avez inscrit {joueurs} joueurs.")
            await ctx.send(f"Le nombre de joueurs doit être supérieur ou égal à 5 ! Vous avez inscrit {joueurs} joueurs.", ephemeral=True)
            return
        elif loups > 100:
            logger.warning(f"Le pourcentage de loup doit être inférieur ou égal à 100%! Vous avez inscrit {loups}% de loups.")
            await ctx.send(f"Le pourcentage de loup doit être inférieur ou égal à 100%! Vous avez inscrit {loups}% de loups.", ephemeral=True)
            return
        else:
            await request_consent(ctx, joueurs)

# Fonction pour demander le consentement aux joueurs
async def request_consent(ctx: SlashContext, joueurs: int):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        logger.warning("L'utilisateur n'est pas dans un salon vocal.")
        await ctx.send("Vous devez être dans un salon vocal pour démarrer une partie.", ephemeral=True)
        return
    
    members = voice_channel.members
    if len(members) < joueurs:
        logger.warning(f"Nombre insuffisant de joueurs dans le salon vocal. {len(members)} présents, {joueurs} nécessaires.")
        await ctx.send(f"Il n'y a pas assez de joueurs dans le salon vocal. {len(members)} présents, {joueurs} nécessaires.", ephemeral=True)
        return

    consented_players = []

    for player in members:
        try:
            logger.info(f"Demande de consentement à {player.display_name}")
            consented = await request_consent_dm(player)
            if consented:
                consented_players.append(player)
        except Exception as e:
            logger.error(f"Impossible d'envoyer un DM à {player.display_name}: {e}")

    if len(consented_players) >= joueurs:
        await start_game(ctx, consented_players)
    else:
        logger.warning(f"Nombre de joueurs ayant consenti insuffisant. {len(consented_players)} consentis, {joueurs} nécessaires.")
        await ctx.send(f"Nombre de joueurs ayant consenti insuffisant. {len(consented_players)} consentis, {joueurs} nécessaires.", ephemeral=True)

# Fonction pour demander le consentement en message privé
async def request_consent_dm(player):
    consented = False
    message = await player.send("Voulez-vous participer à une partie de Loups Garous ? Appuyez sur ✅ pour accepter ou ❌ pour refuser.")

    def check(reaction, user):
        return user == player and reaction.message.id == message.id and str(reaction.emoji) in ["✅", "❌"]

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "✅":
            consented = True
    except Exception as e:
        logger.error(f"Erreur lors de l'attente de la réaction de {player.display_name}: {e}")

    return consented

# Fonction pour démarrer la partie
async def start_game(ctx: SlashContext, players):
    logger.info("Démarrage de la partie...")
    joueurs = len(players)
    loups = 30  # Pour l'instant, fixons le pourcentage de loups à 30%
    nb_loups = round(joueurs * (loups / 100))
    wolves = random.sample(players, nb_loups)
    
    for player in players:
        role = "Loup" if player in wolves else "Villageois"
        logger.info(f"Rôle attribué à {player.display_name}: {role}")
        await ctx.send(f"DM envoyé à {player.display_name} avec son rôle de {role}.")
        try:
            await player.send(f"Vous êtes un {role} pour cette partie de Loups Garous.")
        except Exception as e:
            logger.error(f"Impossible d'envoyer un DM à {player.display_name}: {e}")
            await ctx.send(f"Impossible d'envoyer un message privé à {player.display_name}. Assurez-vous que les messages privés sont activés.", ephemeral=True)

    await ctx.send(f"Démarrage de la partie avec {joueurs} joueurs et {nb_loups} loups.")

# Démarrage du bot
bot.start()
