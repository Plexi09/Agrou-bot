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

# Constantes
MIN_JOUEURS = 5
POURCENTAGE_LOUPS = 30

# Fonction appelée lorsque le bot est prêt
@listen()
async def on_ready():
    logger.info(f'Connecté en tant que {bot.user}')

# Commande pour démarrer une partie de Loups Garous
@slash_command(name="warewolf", description="Démarre une partie de Loups Garous avec les membres de votre salon vocal.")
@slash_option(name="force", description="Force le démarrage de la partie", opt_type=OptionType.BOOLEAN, required=False)
async def warewolf_function(ctx: SlashContext, force: bool = False):
    logger.info(f'Commande /warewolf appelée par {ctx.author.display_name} avec force={force}.')

    if ctx.author.voice is None:
        await ctx.send("Vous devez être dans un salon vocal pour démarrer une partie.", ephemeral=True)
        return

    voice_channel = ctx.author.voice.channel
    response = await bot.http.request("GET", f"/channels/{voice_channel.id}/users")  # Get the members in the voice channel
    channel_members = await response.json()  # Parse the response as JSON
    members = [bot.get_user(member["id"]) for member in channel_members]  # Get the User objects
    joueurs = len(members)  # Count the number of members in the voice channel

    if force:
        logger.info("Démarrage de la partie forcé !")
        await ctx.send("🚨 Démarrage de la partie forcé ! Attendez-vous à des erreurs si les conditions de partie ne sont pas atteintes. 🚨")
        await start_game(ctx, members)
        return

    if joueurs < MIN_JOUEURS:
        logger.warning(f"Le nombre de joueurs doit être supérieur ou égal à {MIN_JOUEURS} ! {joueurs} présents.")
        await ctx.send(f"Le nombre de joueurs doit être supérieur ou égal à {MIN_JOUEURS} ! {joueurs} présents.", ephemeral=True)
        return

    await start_game(ctx, members)

# Fonction pour démarrer la partie
async def start_game(ctx: SlashContext, players):
    logger.info("Démarrage de la partie...")
    joueurs = len(players)
    nb_loups = round(joueurs * (POURCENTAGE_LOUPS / 100))
    wolves = random.sample(players, nb_loups)
    
    for player in players:
        role = "Loup" if player in wolves else "Villageois"
        logger.info(f"Rôle attribué à {player.display_name}: {role}")
        await ctx.send(f"DM envoyé à {player.display_name} avec son rôle de {role}.", ephemeral=True)
        try:
            await player.send(f"Vous êtes un {role} pour cette partie de Loups Garous.")
        except Exception as e:
            logger.error(f"Impossible d'envoyer un DM à {player.display_name}: {e}")
            await ctx.send(f"Impossible d'envoyer un message privé à {player.display_name}. Assurez-vous que les messages privés sont activés.", ephemeral=True)

    await ctx.send(f"Démarrage de la partie avec {joueurs} joueurs et {nb_loups} loups.")
    running = True
    return running

# Commande pour voter un joueur
@slash_command(name="vote", description="Vote pour un joueur à éliminer.")
@slash_option(name="joueur", description="Joueur à éliminer", opt_type=OptionType.USER, required=True)
async def vote_function(ctx: SlashContext, joueur, running):
    if running:
        logger.info(f'Commande /vote appelée par {ctx.author.display_name} pour {joueur.display_name}.')

        # À compléter : gestion des votes et élimination des joueurs
    if not running:
        await ctx.send("Aucune partie en cours.", ephemeral=True)

# Commande pour afficher les joueurs vivants
@slash_command(name="joueurs", description="Affiche la liste des joueurs vivants.")
async def joueurs_function(ctx: SlashContext, running):
    if running:
        logger.info(f'Commande /joueurs appelée par {ctx.author.display_name}.')

    # À compléter : affichage des joueurs vivants

    if not running:
        await ctx.send("Aucune partie en cours.", ephemeral=True)

# Démarrage du bot
bot.start()
