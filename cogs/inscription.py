import discord
from discord.ext import commands
from discord import app_commands

# ==========================================
# 1. LES MODALS INDÉPENDANTS (5 CHAMPS MAX)
# ==========================================

class ModalJeux1(discord.ui.Modal, title="Partie 1 : Vos Pseudos"):
    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2", style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2", style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io", style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="ID Riot (Valorant)", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        # TODO: Enregistrement gspread pour la partie 1
        await interaction.response.send_message("✅ Partie 1 enregistrée avec succès ! Sélectionne l'étape 2 dans le menu pour continuer.", ephemeral=True)


class ModalJeux2(discord.ui.Modal, title="Partie 2 : Vos Pseudos"):
    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck", style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches", style=discord.TextStyle.short)
    pseudo_ohbabykart = discord.ui.TextInput(label="Pseudo Oh Baby Kart", style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="ID Brawl Stars", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        # TODO: Enregistrement gspread pour la partie 2
        await interaction.response.send_message("✅ Partie 2 enregistrée avec succès ! Sélectionne l'étape 3 dans le menu pour continuer.", ephemeral=True)


class ModalProfil(discord.ui.Modal, title="Partie 3 : Votre Profil"):
    meilleurs_jeux = discord.ui.TextInput(label="Ton meilleur jeu", style=discord.TextStyle.short, placeholder="Tetris.io, Smite 2, ...")
    pire_jeux = discord.ui.TextInput(label="Ton pire jeu", style=discord.TextStyle.short, placeholder="Oh Baby Kart, ...")
    remarques = discord.ui.TextInput(label="Remarques", style=discord.TextStyle.long, placeholder="Quelque chose à ajouter ?", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # TODO: Enregistrement gspread pour la partie 3
            
            # 🔐 Le lien s'affiche ICI automatiquement quand il valide le profil
            OAUTH_URL = "https://discord.com/oauth2/authorize?client_id=..." # <-- Mets ton vrai lien ici
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="🔐 Étape Finale : Valider mon Discord", url=OAUTH_URL, style=discord.ButtonStyle.link))
            
            await interaction.response.send_message(
                content="📊 **Profil enregistré avec succès !**\n\nPour finaliser complètement ton inscription à la Pixelot Cup, clique sur le bouton ci-dessous :",
                view=view,
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)


# ==========================================
# 2. LE MENU DÉROULANT D'INSCRIPTION
# ==========================================

class MenuInscription(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1. Pseudos (Partie 1)", description="Smite 2, Legion TD 2, Tetris, Riot ID", emoji="⚔️"),
            discord.SelectOption(label="2. Pseudos (Partie 2)", description="Puck, Quick Matches, Kart, Brawl Stars", emoji="🕹️"),
            discord.SelectOption(label="3. Mon Profil & Avis", description="Tes tops/flops et remarques", emoji="📊"),
            discord.SelectOption(label="4. Lier mon compte Discord", description="Étape finale d'authentification OAuth2", emoji="🔐")
        ]
        super().__init__(placeholder="Choisis une étape pour t'inscrire...", min_values=1, max_values=1, options=options, custom_id="select_inscription")

    async def callback(self, interaction: discord.Interaction):
        choix = self.values[0]

        if choix == "1. Pseudos (Partie 1)":
            await interaction.response.send_modal(ModalJeux1())
            
        elif choix == "2. Pseudos (Partie 2)":
            await interaction.response.send_modal(ModalJeux2())
            
        elif choix == "3. Mon Profil & Avis":
            await interaction.response.send_modal(ModalProfil())
            
        elif choix == "4. Lier mon compte Discord":
            # 🔐 Le lien est AUSSI disponible ici en accès direct dans le menu
            OAUTH_URL = "https://discord.com/oauth2/authorize?client_id=..." # <-- Mets ton vrai lien ici
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="🔗 Lien de connexion Discord", url=OAUTH_URL, style=discord.ButtonStyle.link))
            
            await interaction.response.send_message(
                content="⚠️ **Clique sur le bouton ci-dessous pour lier officiellement ton compte Discord à ton inscription :**",
                view=view,
                ephemeral=True
            )


class InscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # On ajoute le menu déroulant à la vue principale pour qu'il soit persistant
        self.add_item(MenuInscription())


# ==========================================
# 3. LE COG PRINCIPAL (COMMANDE SLASH)
# ==========================================

class Inscription(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lancer_panneau", description="Affiche le panneau d'inscription avec menu déroulant")
    @app_commands.default_permissions(administrator=True)
    async def lancer_panneau(self, interaction: discord.Interaction):
        
        ID_SALON_INSCRIPTION = 1509961077696237778  
        if interaction.channel_id != ID_SALON_INSCRIPTION:
            await interaction.response.send_message("⚠️ Vous n'êtes pas dans le salon d'inscription !", ephemeral=True)
            return

        await interaction.response.send_message("⌛ Génération du panneau...", ephemeral=True)

        embed = discord.Embed(
            title="🏆 Inscriptions à la Pixelot Cup 2026",
            description=(
                "Bienvenue sur le panneau d'inscription officiel.\n\n"
                "📋 **Instructions :**\n"
                "Utilise le **menu déroulant ci-dessous** pour compléter les différentes étapes à ton rythme.\n"
                "Tu dois obligatoirement soumettre les étapes 1, 2, 3 et lier ton compte (étape 4) pour valider ton inscription !"
            ),
            color=discord.Color.gold()
        )

        await interaction.channel.send(embed=embed, view=InscriptionView())

async def setup(bot):
    await bot.add_cog(Inscription(bot))