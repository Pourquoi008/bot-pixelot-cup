import discord
from discord.ext import commands
from discord import app_commands

# ==========================================
# 1. LES 3 MODALS EN CHAÎNE (MAX 4-5 CHAMPS CHACUN)
# ==========================================

# ÉTAPE 3 : Profil & Avis (Lancé après l'Étape 2)
class InscriptionModalEtape3(discord.ui.Modal, title="Inscription (3/3) : Profil"):
    meilleurs_jeux = discord.ui.TextInput(label="Ton meilleur jeu", style=discord.TextStyle.short, placeholder="Tetris.io, Smite 2, ...")
    pire_jeux = discord.ui.TextInput(label="Ton pire jeu", style=discord.TextStyle.short, placeholder="Oh Baby Kart, A few quick matches, ...")
    remarques = discord.ui.TextInput(label="Remarques", style=discord.TextStyle.long, placeholder="Si tu as des remarques, c'est ici !", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # 💡 C'est ICI à la toute fin que tu as TOUTES les données prêtes à être envoyées à ta Google Sheet !
            # Tu pourras récupérer : self.meilleurs_jeux.value, etc.
            
            # Message final avec ton lien OAuth2 pour lier le compte Discord
            OAUTH_URL = "https://discord.com/oauth2/authorize?client_id=..." # <-- Mets ton vrai lien ici
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="🔐 Étape Finale : Valider mon Discord", url=OAUTH_URL, style=discord.ButtonStyle.link))
            
            await interaction.response.send_message(
                content=f"📊 **Pseudos et profil enregistrés avec succès !**\n\nPour finaliser complètement ton inscription à la Pixelot Cup, clique sur le bouton ci-dessous :",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur Étape 3 : {e}", ephemeral=True)


# ÉTAPE 2 : Suite des jeux (Lancé après l'Étape 1)
class InscriptionModalEtape2(discord.ui.Modal, title="Inscription (2/3) : Jeux Arcade"):
    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck", style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches", style=discord.TextStyle.short)
    pseudo_ohbabykart = discord.ui.TextInput(label="Pseudo Oh Baby Kart", style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="ID Brawl Stars", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Dès que l'Étape 2 est envoyée, on enchaîne DIRECTEMENT sur l'Étape 3
            await interaction.response.send_modal(InscriptionModalEtape3())
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur Étape 2 : {e}", ephemeral=True)


# ÉTAPE 1 : Début du formulaire (Lancé par le bouton vert)
class InscriptionModal(discord.ui.Modal, title="Inscription (1/3) : Jeux"):
    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2", style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2", style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io", style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="ID Riot", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Dès que l'Étape 1 est envoyée, on enchaîne DIRECTEMENT sur l'Étape 2
            await interaction.response.send_modal(InscriptionModalEtape2())
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur Étape 1 : {e}", ephemeral=True)


# ==========================================
# 2. LA VUE AVEC LE BOUTON VERT UNIQUE
# ==========================================

class InscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="S'inscrire à la Cup", style=discord.ButtonStyle.green, emoji="📝", custom_id="btn_inscription")
    async def bouton_inscription(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        # 🔒 Ta sécurité de salon avec ton ID de salon #inscription
        ID_SALON_INSCRIPTION = 1509961077696237778  
        
        if interaction.channel_id != ID_SALON_INSCRIPTION:
            await interaction.response.send_message("⚠️ Vous n'êtes pas dans le salon d'inscription !", ephemeral=True)
            return

        # On lance la première étape !
        await interaction.response.send_modal(InscriptionModal())


# ==========================================
# 3. LE COG PRINCIPAL (COMMANDE SLASH)
# ==========================================

class Inscription(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lancer_panneau", description="Affiche le panneau avec le bouton d'inscription")
    @app_commands.default_permissions(administrator=True)
    async def lancer_panneau(self, interaction: discord.Interaction):
        
        await interaction.response.send_message("⌛ Génération du panneau...", ephemeral=True)

        embed = discord.Embed(
            title="🏆 Inscriptions à la Pixelot Cup 2026",
            description=(
                "Prêt à relever le défi et à affronter les autres joueurs ?\n\n"
                "📌 **Comment s'inscrire ?**\n"
                "1️⃣ Cliquez sur le bouton vert ci-dessous.\n"
                "2️⃣ Remplis tes pseudos pour l'ensemble des jeux (3 étapes rapides).\n"
                "3️⃣ Connecte ton compte Discord pour valider ton inscription.\n\n"
                "⚠️ *Veille à fournir tes vrais identifiants pour qu'on puisse te retrouver en jeu !*"
            ),
            color=discord.Color.gold()
        )

        await interaction.channel.send(embed=embed, view=InscriptionView())

async def setup(bot):
    await bot.add_cog(Inscription(bot))