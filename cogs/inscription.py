import discord
from discord.ext import commands
from discord import app_commands

# ==========================================
# 1. LES MODALS INDÉPENDANTS
# ==========================================

class ModalJeux1(discord.ui.Modal, title="Partie 1 : Vos Pseudos"):
    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2", style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2", style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io", style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="ID Riot (Valorant)", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        # ✨ LA MAGIE EST ICI : Le bot récupère tout seul le gars qui a répondu !
        joueur_discord = interaction.user.name  # Ex: "mathis_noel"
        id_discord = interaction.user.id        # Ex: 1509961077696237778
        
        # TODO: Quand on liera Google Sheets, on enverra : joueur_discord, self.pseudo_smite2.value, etc.
        print(f"🎮 [Partie 1] {joueur_discord} ({id_discord}) a rempli ses premiers pseudos.")
        
        await interaction.response.send_message("✅ Partie 1 enregistrée avec succès ! Sélectionne l'étape 2 dans le menu pour continuer.", ephemeral=True)


class ModalJeux2(discord.ui.Modal, title="Partie 2 : Vos Pseudos"):
    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck", style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches", style=discord.TextStyle.short)
    pseudo_ohbabykart = discord.ui.TextInput(label="Pseudo Oh Baby Kart", style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="ID Brawl Stars", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        joueur_discord = interaction.user.name
        
        print(f"🕹️ [Partie 2] {joueur_discord} a rempli la suite de ses pseudos.")
        await interaction.response.send_message("✅ Partie 2 enregistrée avec succès ! Sélectionne l'étape 3 dans le menu pour continuer.", ephemeral=True)


class ModalProfil(discord.ui.Modal, title="Partie 3 : Votre Profil"):
    meilleurs_jeux = discord.ui.TextInput(label="Ton meilleur jeu", style=discord.TextStyle.short, placeholder="Tetris.io, Smite 2, ...")
    pire_jeux = discord.ui.TextInput(label="Ton pire jeu", style=discord.TextStyle.short, placeholder="Oh Baby Kart, ...")
    remarques = discord.ui.TextInput(label="Remarques", style=discord.TextStyle.long, placeholder="Quelque chose à ajouter ?", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        joueur_discord = interaction.user.name
        
        print(f"📊 [Partie 3] {joueur_discord} a terminé son profil.")
        
        # Message de confirmation finale ultra propre
        await interaction.response.send_message(
            content=f"🏆 **Inscription validée !**\n\nMerci pour ton inscription, toutes tes informations ont bien été liées à ton compte Discord (**{joueur_discord}**).",
            ephemeral=True
        )


# ==========================================
# 2. LE MENU DÉROULANT D'INSCRIPTION
# ==========================================

class MenuInscription(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1. Pseudos (Partie 1)", description="Smite 2, Legion TD 2, Tetris, Riot ID", emoji="⚔️"),
            discord.SelectOption(label="2. Pseudos (Partie 2)", description="Puck, Quick Matches, Kart, Brawl Stars", emoji="🕹️"),
            discord.SelectOption(label="3. Mon Profil & Avis", description="Tes tops/flops et remarques", emoji="📊")
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


class InscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
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
                "Le bot liera automatiquement tes réponses à ton compte Discord actuel !"
            ),
            color=discord.Color.gold()
        )

        await interaction.channel.send(embed=embed, view=InscriptionView())

async def setup(bot):
    await bot.add_cog(Inscription(bot))