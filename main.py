import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

# Récupération du token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        # 1. Enregistrement de la vue persistante ICI (L'endroit officiel et sécurisé)
        try:
            from cogs.inscription import InscriptionView
            self.add_view(InscriptionView())
            print("🔒 Bouton d'inscription enregistré et persistant !", flush=True)
        except Exception as e:
            print(f"❌ Erreur critique enregistrement vue persistante : {e}", flush=True)

        # 2. Chargement des Cogs
        for extension in ['inscription', 'bienvenue','ping_role','teams']:
            try:
                await self.load_extension(f'cogs.{extension}')
                print(f"✅ Cog '{extension}' chargé.", flush=True)
            except Exception as e:
                print(f"❌ Impossible de charger le cog {extension} : {e}", flush=True)

        # 3. La synchro des commandes Slash
        print("🔄 Synchronisation des commandes slash...", flush=True)
        try:
            synced = await self.tree.sync()
            print(f"✅ {len(synced)} commande(s) synchronisée(s)", flush=True)
        except Exception as e:
            print(f"❌ Erreur de synchronisation : {e}", flush=True)

# Configuration du bot avec Intents.all()
intents = discord.Intents.all()
bot = Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Ce print s'affichera instantanément dès que le bot a fini de charger les données Discord
    print(f"🚀 Connecté et opérationnel en tant que {bot.user}", flush=True)

# Lancement du serveur de maintien en vie et du bot
keep_alive()
bot.run(token=token)