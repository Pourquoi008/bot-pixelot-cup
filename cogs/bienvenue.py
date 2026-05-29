import discord
from discord.ext import commands

class Bienvenue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 🆔 Remplace par le véritable ID de ton salon textuel de bienvenue
        self.WELCOME_CHANNEL_ID = 1508746654004543521 
        self.INSCRIPTION_CHANNEL_ID = 1509961077696237778

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # 1. On récupère le salon grâce à son ID brut
        channel = self.bot.get_channel(self.WELCOME_CHANNEL_ID)
        
        # Sécurité au cas où l'ID est mauvais ou le bot n'a pas accès au salon
        if channel is None:
            print(
                f"⚠️ Impossible de trouver le salon avec l'ID {self.WELCOME_CHANNEL_ID}"
            )
            return

        # Création de l'embed principal
        embed = discord.Embed(
            title=f"🎮 Bienvenue dans la Pixelot Cup, {member.name} !",
            description=(
                f"📌 Rendez-vous dans le salon <#{self.INSCRIPTION_CHANNEL_ID}> pour t'inscrire !"
            ),
            color=discord.Color.gold()
        )

        # 🕹️ Liste des Jeux de l'affiche (séparés en deux colonnes propres)
        embed.add_field(
            name="⚔️ Les Jeux", 
            value="• Valorant 🎯\n• Brawl Stars 💥\n• Smite 2 ⚡\n• Legion TD 2 🛡️", 
            inline=True
        )
        
        embed.add_field(
            name="🕹️ Les Jeux", 
            value="• Tetris.io 🧩\n• Puck 🏒\n• Oh Baby Kart 🏎️\n• A few quick matches ⚔️", 
            inline=True
        )

        # L'avatar du joueur en grand en dessous
        embed.set_image(url=member.display_avatar.url)
        
        # Un footer plus pro axé sur l'événement
        embed.set_footer(text="Pixelot © 2026 • Que le meilleur gagne !")

        # Envoi du message
        await channel.send(content=f"Hey {member.mention} est arrivé !", embed=embed)

# Fonction obligatoire pour charger le Cog
async def setup(bot):
    await bot.add_cog(Bienvenue(bot))