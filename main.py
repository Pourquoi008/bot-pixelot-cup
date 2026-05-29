import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

# Récupération du token dans un fichier .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

class Bot(commands.Bot):
    async def setup_hook(self):
        # 1. Chargement des Cogs (vérifie bien le nom de tes fichiers en minuscules)
        for extension in ['inscription', 'bienvenue']:
            try:
                await self.load_extension(f'cogs.{extension}')
                print(f"✅ Cog '{extension}' chargé.")
            except Exception as e:
                print(f"❌ Impossible de charger le cog {extension} : {e}")

        # 2. La synchro des commandes Slash se fait ICI, une seule fois au démarrage
        print("🔄 Synchronisation des commandes slash...")
        try:
            synced = await self.tree.sync()
            print(f"✅ {len(synced)} commande(s) synchronisée(s)")
        except Exception as e:
            print(f"❌ Erreur de synchronisation : {e}")

# Utilisation de Intents.all() -> Parfait puisque tu as tout coché sur le portail dev
intents = discord.Intents.all()
bot = Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🚀 Connecté et opérationnel en tant que {bot.user}")

# Lancement du serveur de maintien en vie et du bot
keep_alive()
bot.run(token=token)