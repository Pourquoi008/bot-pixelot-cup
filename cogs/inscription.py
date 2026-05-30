import discord
from discord.ext import commands
from discord import app_commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# ==========================================
# CONTEXTE & CONNEXION GOOGLE SHEETS
# ==========================================

def get_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # 🔐 On récupère le secret injecté par le fichier YML
    creds_json = os.getenv("GOOGLE_CREDS")
    if not creds_json:
        raise ValueError("❌ Erreur : La variable d'environnement GOOGLE_CREDS est introuvable !")
        
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Cherche le fichier Google Sheets par son nom exact
    return client.open("Inscriptions Pixelot Cup").sheet1

def update_or_insert_player(discord_id, discord_name, column_data):
    """Cherche un joueur par son ID Discord et met à jour ses données, ou crée une ligne."""
    sheet = get_sheets_client()
    
    # Créer les entêtes si le fichier est tout neuf
    if not sheet.cell(1, 1).value:
        headers = [
            "ID Discord", "Pseudo Discord", "Smite 2", "Legion TD 2", 
            "Tetris.io", "Riot ID", "Puck", "A few quick matches", 
            "Oh Baby Kart", "Brawl Stars", "Meilleur Jeu", "Pire Jeu", "Remarques"
        ]
        sheet.insert_row(headers, 1)

    # Chercher si l'ID du joueur existe déjà (colonne A)
    cell = sheet.find(str(discord_id), in_column=1)
    
    if cell:
        # Le joueur existe, on met à jour les colonnes spécifiques fournies
        for col_name, value in column_data.items():
            headers = sheet.row_values(1)
            col_index = headers.index(col_name) + 1
            sheet.update_cell(cell.row, col_index, value)
    else:
        # Nouveau joueur : on crée une nouvelle ligne avec ses identifiants de base
        new_row = [str(discord_id), discord_name] + [""] * 11
        sheet.append_row(new_row)
        
        # On relance la fonction pour remplir les données maintenant que la ligne existe
        cell = sheet.find(str(discord_id), in_column=1)
        for col_name, value in column_data.items():
            headers = sheet.row_values(1)
            col_index = headers.index(col_name) + 1
            sheet.update_cell(cell.row, col_index, value)

# ==========================================
# 2. LES MODALS INDÉPENDANTS
# ==========================================

class ModalJeux1(discord.ui.Modal, title="Partie 1 : Vos Pseudos"):
    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2", style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2", style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io", style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="ID Riot (Valorant)", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data = {
                "Smite 2": self.pseudo_smite2.value,
                "Legion TD 2": self.pseudo_legiontd2.value,
                "Tetris.io": self.pseudo_tetrisio.value,
                "Riot ID": self.id_riot.value
            }
            update_or_insert_player(interaction.user.id, interaction.user.name, data)
            await interaction.response.send_message("✅ Partie 1 enregistrée sur le Google Sheets ! Sélectionne l'étape 2 dans le menu.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)


class ModalJeux2(discord.ui.Modal, title="Partie 2 : Vos Pseudos"):
    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck", style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches", style=discord.TextStyle.short)
    pseudo_ohbabykart = discord.ui.TextInput(label="Pseudo Oh Baby Kart", style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="ID Brawl Stars", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data = {
                "Puck": self.pseudo_puck.value,
                "A few quick matches": self.pseudo_afewquickmatches.value,
                "Oh Baby Kart": self.pseudo_ohbabykart.value,
                "Brawl Stars": self.id_brawlstars.value
            }
            update_or_insert_player(interaction.user.id, interaction.user.name, data)
            await interaction.response.send_message("✅ Partie 2 enregistrée sur le Google Sheets ! Sélectionne l'étape 3 dans le menu.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)


class ModalProfil(discord.ui.Modal, title="Partie 3 : Votre Profil"):
    meilleurs_jeux = discord.ui.TextInput(label="Ton meilleur jeu", style=discord.TextStyle.short, placeholder="Tetris.io, Smite 2, ...")
    pire_jeux = discord.ui.TextInput(label="Ton pire jeu", style=discord.TextStyle.short, placeholder="Oh Baby Kart, ...")
    remarques = discord.ui.TextInput(label="Remarques", style=discord.TextStyle.long, placeholder="Quelque chose à ajouter ?", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data = {
                "Meilleur Jeu": self.meilleurs_jeux.value,
                "Pire Jeu": self.pire_jeux.value,
                "Remarques": self.remarques.value
            }
            update_or_insert_player(interaction.user.id, interaction.user.name, data)
            
            await interaction.response.send_message(
                content=f"🏆 **Inscription validée sur le Sheets !**\n\nMerci, toutes tes informations ont été liées à ton compte Discord (**{interaction.user.name}**).",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)

# ==========================================
# 3. LE MENU DÉROULANT D'INSCRIPTION
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
# 4. LE COG PRINCIPAL (COMMANDE SLASH)
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
                "Le bot liera automatiquement tes réponses à ton compte Discord actuel sur notre tableau de suivi !"
            ),
            color=discord.Color.gold()
        )
        await interaction.channel.send(embed=embed, view=InscriptionView())

async def setup(bot):
    await bot.add_cog(Inscription(bot))