import discord
from discord.ext import commands
from discord import app_commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import asyncio
from datetime import datetime
import zoneinfo # Pour gérer l'heure française proprement

# ==========================================
# CONTEXTE & CONNEXION GOOGLE SHEETS
# ==========================================

def get_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDS")
    if not creds_json:
        raise ValueError("❌ Erreur : La variable d'environnement GOOGLE_CREDS est introuvable !")
        
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Inscriptions Pixelot Cup").sheet1

def update_or_insert_player(discord_id, discord_name, column_data):
    sheet = get_sheets_client()
    
    # 📅 Récupération du timestamp au format : JJ/MM/AAAA HH:MM:SS (Heure de Paris)
    tz_paris = zoneinfo.ZoneInfo("Europe/Paris")
    timestamp = datetime.now(tz_paris).strftime("%d/%m/%Y %H:%M:%S")

    # Créer les entêtes si le fichier est tout neuf (avec la colonne Timestamp en premier)
    if not sheet.cell(1, 1).value:
        headers = [
            "Date d'inscription", "ID Discord", "Pseudo Discord", "Smite 2", 
            "Legion TD 2", "Tetris.io", "Riot ID", "Puck", "A few quick matches", 
            "Oh Baby Kart", "Brawl Stars", "Meilleur Jeu", "Pire Jeu", "Remarques"
        ]
        sheet.insert_row(headers, 1)

    # Désormais, l'ID Discord se trouve en colonne B (in_column=2)
    cell = sheet.find(str(discord_id), in_column=2)
    
    if cell:
        # Le joueur existe, on met à jour ses colonnes
        for col_name, value in column_data.items():
            headers = sheet.row_values(1)
            try:
                col_index = headers.index(col_name) + 1
                sheet.update_cell(cell.row, col_index, value)
            except ValueError:
                pass
    else:
        # Nouveau joueur : on crée une nouvelle ligne avec le Timestamp en premier (colonne A)
        # Suivi de son ID (colonne B) et son Pseudo (colonne C)
        new_row = [timestamp, str(discord_id), discord_name] + [""] * 11
        sheet.append_row(new_row)
        
        # On recherche la ligne pour ajouter les pseudos spécifiques du formulaire actuel
        cell = sheet.find(str(discord_id), in_column=2)
        if cell:
            for col_name, value in column_data.items():
                headers = sheet.row_values(1)
                try:
                    col_index = headers.index(col_name) + 1
                    sheet.update_cell(cell.row, col_index, value)
                except ValueError:
                    pass

# ==========================================
# 1.5 BOUTONS DE TRANSITION RAPIDE (ÉPHÉMÈRES)
# ==========================================

class ActionEtapeSuivante(discord.ui.View):
    def __init__(self, prochaine_etape):
        super().__init__(timeout=60)
        self.prochaine_etape = prochaine_etape

    @discord.ui.button(label="Continuer l'inscription ➡️", style=discord.ButtonStyle.green)
    async def bouton_suivant(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.prochaine_etape == 2:
            await interaction.response.send_modal(ModalJeux2())
        elif self.prochaine_etape == 3:
            await interaction.response.send_modal(ModalProfil())

# ==========================================
# 2. LES MODALS INDÉPENDANTS
# ==========================================

class ModalJeux1(discord.ui.Modal, title="Partie 1 : Vos Pseudos"):
    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2", style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2", style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io", style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="ID Riot (Valorant)", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = {
                "Smite 2": self.pseudo_smite2.value,
                "Legion TD 2": self.pseudo_legiontd2.value,
                "Tetris.io": self.pseudo_tetrisio.value,
                "Riot ID": self.id_riot.value
            }
            await asyncio.to_thread(update_or_insert_player, interaction.user.id, interaction.user.name, data)
            
            await interaction.followup.send(
                content="✅ **Partie 1 enregistrée !** Clique ci-dessous pour passer à la suite :", 
                view=ActionEtapeSuivante(prochaine_etape=2), 
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)


class ModalJeux2(discord.ui.Modal, title="Partie 2 : Vos Pseudos"):
    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck", style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches", style=discord.TextStyle.short)
    pseudo_ohbabykart = discord.ui.TextInput(label="Pseudo Oh Baby Kart", style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="ID Brawl Stars", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = {
                "Puck": self.pseudo_puck.value,
                "A few quick matches": self.pseudo_afewquickmatches.value,
                "Oh Baby Kart": self.pseudo_ohbabykart.value,
                "Brawl Stars": self.id_brawlstars.value
            }
            await asyncio.to_thread(update_or_insert_player, interaction.user.id, interaction.user.name, data)
            
            await interaction.followup.send(
                content="✅ **Partie 2 enregistrée !** Clique ci-dessous pour donner ton profil :", 
                view=ActionEtapeSuivante(prochaine_etape=3), 
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)


class ModalProfil(discord.ui.Modal, title="Partie 3 : Votre Profil"):
    meilleurs_jeux = discord.ui.TextInput(label="Ton meilleur jeu", style=discord.TextStyle.short, placeholder="Tetris.io, Smite 2, ...")
    pire_jeux = discord.ui.TextInput(label="Ton pire jeu", style=discord.TextStyle.short, placeholder="Oh Baby Kart, ...")
    remarques = discord.ui.TextInput(label="Remarques", style=discord.TextStyle.long, placeholder="Quelque chose à ajouter ?", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = {
                "Meilleur Jeu": self.meilleurs_jeux.value,
                "Pire Jeu": self.pire_jeux.value,
                "Remarques": self.remarques.value
            }
            await asyncio.to_thread(update_or_insert_player, interaction.user.id, interaction.user.name, data)
            
            await interaction.followup.send(
                content=f"🏆 **Inscription validée !**\n\nMerci, toutes tes informations ont été liées à ton compte Discord (**{interaction.user.name}**).",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)

# ==========================================
# 3. LE GROS BOUTON UNIQUE ET PERSISTANT
# ==========================================

class InscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="S'inscrire 🏆", style=discord.ButtonStyle.green, custom_id="btn_inscription_unique")
    async def bouton_inscription(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModalJeux1())

# ==========================================
# 4. LE COG PRINCIPAL (COMMANDE SLASH)
# ==========================================

class Inscription(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lancer_panneau", description="Affiche le panneau avec le bouton unique d'inscription")
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
                "Clique sur le bouton **S'inscrire 🏆** ci-dessous pour lancer le formulaire.\n"
                "Laisse-toi guider à travers les étapes pour lier tes pseudos à ton compte Discord actuel !"
            ),
            color=discord.Color.gold()
        )
        await interaction.channel.send(embed=embed, view=InscriptionView())

async def setup(bot):
    await bot.add_cog(Inscription(bot))