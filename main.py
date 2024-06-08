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

# Configurer le logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    print(f'Connecté en tant que {bot.user}')

# Commande pour démarrer une partie de Loups Garous
@slash_command(name="warewolf", description="Démarre une partie de Loups Garous avec les membres de votre salon vocal.")
@slash_option(name="joueurs", description="Nombre de joueurs", opt_type=OptionType.INTEGER, required=True)
@slash_option(name="loups", description="Proportion de loup en %", opt_type=OptionType.INTEGER, required=False)
@slash_option(name="force", description="Force le démarrage de la partie", opt_type=OptionType.BOOLEAN, required=False)
async def warewolf_function(ctx: SlashContext, joueurs: int, loups: int = 30, force: bool = False):
    # Si la partie est forcée
    if force:
        await ctx.send("🚨 Démarrage de la partie forcé ! Attendez-vous à des erreurs si les conditions de partie ne sont pas atteintes. 🚨")
        await start_game(ctx, joueurs, loups, force)
        return

    # Si la partie n'est pas forcée
    if not force:
        # Vérifie les conditions de démarrage
        if joueurs < 5:
            await ctx.send(f"Le nombre de joueurs doit être supérieur ou égal à 5 ! Vous avez inscrit {joueurs} joueurs.", ephemeral=True)
            return
        elif loups > 100:
            await ctx.send(f"Le pourcentage de loup doit être inférieur ou égal à 100%! Vous avez inscrit {loups}% de loups.", ephemeral=True)
            return
        else:
            await start_game(ctx, joueurs, loups, force)

# Fonction pour démarrer la partie
async def start_game(ctx: SlashContext, joueurs: int, loups: int, force: bool):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("Vous devez être dans un salon vocal pour démarrer une partie.", ephemeral=True)
        return
    
    members = voice_channel.members
    if len(members) < joueurs:
        await ctx.send(f"Il n'y a pas assez de joueurs dans le salon vocal. {len(members)} présents, {joueurs} nécessaires.", ephemeral=True)
        return

    nb_loups = round(joueurs * (loups / 100))
    players = random.sample(members, joueurs)
    wolves = random.sample(players, nb_loups)
    
    for player in players:
        role = "Loup" if player in wolves else "Villageois"
        await player.send(f"Vous êtes un {role} pour cette partie de Loups Garous.")

    await ctx.send(f"Démarrage de la partie avec {joueurs} joueurs et {nb_loups} loups.")

# Démarrage du bot
bot.start()
