from dotenv import load_dotenv
from datetime import datetime
import interactions
import asyncio
import logging
import os
from interactions import (
    listen,
    slash_command,
    SlashContext,
    OptionType,
    slash_option
)

# Configurer le logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

# Configuration du bot et des intents
bot = interactions.Client(token=BOT_TOKEN)

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

    # Si la partie n'est pas forcée
    if not force:
        # Vérifie les conditions de démarrage
        if joueurs < 5:
            await ctx.send(f"Le nombre de joueurs doit être supérieur ou égal à 5 ! Vous avez inscrit {joueurs} joueurs.", ephemeral=True)
        elif loups > 100:
            await ctx.send(f"Le pourcentage de loup doit être inférieur ou égal à 100%! Vous avez inscrit {loups}% de loups.", ephemeral=True)
        else:
            await start_game(ctx, joueurs, loups, force)

# Fonction pour démarrer la partie
async def start_game(ctx: SlashContext, joueurs: int, loups: int, force: bool):
    nb_loups = round(joueurs * (loups / 100))
    await ctx.send(f"Démarrage de la partie avec {joueurs} joueurs et {nb_loups} loups.")
    print("Start")

# Démarrage du bot
bot.start()
