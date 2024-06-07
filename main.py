from dotenv import load_dotenv
from datetime import datetime
import interactions
import asyncio
import logging
import os
from interactions import(
    listen,
    slash_command,
    SlashContext,
    OptionType,
    slash_option
)

# Configurer le logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#logging.basicConfig(filename=(f'logs/discord_{timestamp}.log'), level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Chargement des variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

# Configuration du bot et des intents
bot = interactions.Client(token=BOT_TOKEN)

@listen()
async def on_ready():
    print("Ready")
    #logger.info(f'Connecté en tant que {bot.name}')

@slash_command(name="warewolf", description="Démarre une partie de Loups Garous")
@slash_option(
    name="joueurs",
    description="Nombre de joueurs",
    opt_type=OptionType.INTEGER,
    required=True
)
@slash_option(
    name="loups",
    description="Proportion de loup en %",
    opt_type=OptionType.INTEGER,
    required=False
)
@slash_option(
    name="force",
    description="Force le démarrage de la partie",
    opt_type=OptionType.BOOLEAN,
    required=False
)
async def warewolf_function(ctx: SlashContext, joueurs: int, loups: int = 30, force: bool = False):
    if force:
        await ctx.send("🚨 Démarrage de la partie forcé ! Attendez-vous à des erreurs si les conditions de partie ne sont pas atteintes. 🚨")
        await start_game(ctx, joueurs, loups, force)  # Passer les arguments à start_game()

    if not force:
        
        if joueurs < 5:
            await ctx.send(f"Le nombre de joueurs doit être supérieur ou égal à 5 ! Vous avez inscrit {joueurs} joueurs.", ephemeral=True)
        elif loups > 100:
            await ctx.send(f"Le pourcentage de loup doit être inférieur ou égal à 100%! Vous avez inscrit {loups}% de loups.", ephemeral=True)
        else:
            await start_game(ctx, joueurs, loups, force)  # Passer les arguments à start_game()

async def start_game(ctx: SlashContext, joueurs: int, loups: int, force: bool):
    nb_loups = round(joueurs * (loups / 100))
    await ctx.send(f"Démarrage de la partie avec {joueurs} joueurs et {nb_loups} loups.")
    print("Start")

bot.start()