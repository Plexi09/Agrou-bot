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
    Client
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
        await ctx.send("🚨 Démarrage de la partie forcé ! Attendez-vous à des erreurs si les conditions de partie ne sont pas atteintes. 🚨", ephemeral=True)
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
            await start_game(ctx, joueurs, loups, force)

# Fonction pour démarrer la partie
async def start_game(ctx: SlashContext, joueurs: int, loups: int, force: bool):
    logger.info("Démarrage de la partie...")
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

    nb_loups = round(joueurs * (loups / 100))
    players = random.sample(members, joueurs)
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
