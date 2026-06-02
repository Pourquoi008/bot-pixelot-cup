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
# CONTEXTE & ID UNIQUE DES LOGS
# ==========================================
ID_SALON_LOGS = 1510027206095667341

async def envoyer_log(bot, user, etape, statut="INFO", details=None):
    """Envoie un log en direct dans le salon de tracking (Accessible partout)."""
    channel = bot.get_channel(ID_SALON_LOGS)
    if not channel:
        return

    couleurs = {
        "INFO": discord.Color.blue(),
        "SUCCES": discord.Color.green(),
        "ATTENTION": discord.Color.orange(),
        "ERREUR": discord.Color.red()
    }

    embed = discord.Embed(
        title=f"⏱️ Log Inscription • [{statut}]",
        color=couleurs.get(statut, discord.Color.blue()),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="👤 Utilisateur", value=f"{user.mention} (`{user.name}`)", inline=True)
    embed.add_field(name="📍 Étape / Action", value=f"**{etape}**", inline=True)
    
    if details:
        embed.add_field(name="📝 Données / Infos", value=f"```txt\n{details}\n```", inline=False)
        
    embed.set_footer(text="Pixelot Cup 2026 • Live Tracking")
    await channel.send(embed=embed)


# ==========================================
# CONTEXTE & CONNEXION GOOGLE SHEETS
# ==========================================

def get_sheets_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDS")
    if not creds_json:
        raise ValueError("❌ Erreur : La variable d'environnement GOOGLE_CREDS is introuvable !")
        
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Inscriptions Pixelot Cup").sheet1

def update_or_insert_player(discord_id, discord_name, column_data):
    sheet = get_sheets_client()
    
    tz_paris = zoneinfo.ZoneInfo("Europe/Paris")
    timestamp = datetime.now(tz_paris).strftime("%d/%m/%Y %H:%M:%S")

    if not sheet.cell(1, 1).value:
        headers = [
            "Date d'inscription", "ID Discord", "Pseudo Discord", "Smite 2", 
            "Legion TD 2", "Tetris.io", "Riot ID", "Puck", "A few quick matches", 
            "Oh Baby Kart", "Brawl Stars", "Meilleur Jeu", "Pire Jeu", "Remarques"
        ]
        sheet.insert_row(headers, 1)

    cell = sheet.find(str(discord_id), in_column=2)
    
    if cell:
        for col_name, value in column_data.items():
            headers = sheet.row_values(1)
            try:
                col_index = headers.index(col_name) + 1
                sheet.update_cell(cell.row, col_index, value)
            except ValueError:
                pass
    else:
        new_row = [timestamp, str(discord_id), discord_name] + [""] * 11
        sheet.append_row(new_row)
        
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
    def __init__(self, prochaine_etape, bot):
        super().__init__(timeout=60)
        self.prochaine_etape = prochaine_etape
        self.bot = bot

    @discord.ui.button(label="Continuer l'inscription ➡️", style=discord.ButtonStyle.green)
    async def bouton_suivant(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.prochaine_etape == 2:
            await envoyer_log(self.bot, interaction.user, "Clic Transition", "INFO", "Ouverture de la Partie 2 (ModalJeux2)")
            await interaction.response.send_modal(ModalJeux2(self.bot))
        elif self.prochaine_etape == 3:
            await envoyer_log(self.bot, interaction.user, "Clic Transition", "INFO", "Ouverture de la Partie 3 (ModalProfil)")
            await interaction.response.send_modal(ModalProfil(self.bot))

# ==========================================
# 2. LES MODALS INDÉPENDANTS
# ==========================================

class ModalJeux1(discord.ui.Modal, title="Partie 1 : Vos Pseudos"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2", style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2", style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io", style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="Pseudo Riot (Valorant)", style=discord.TextStyle.short, placeholder="MonPseudo#1234")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        details = (
            f"Smite 2: {self.pseudo_smite2.value}\n"
            f"Legion TD 2: {self.pseudo_legiontd2.value}\n"
            f"Tetris.io: {self.pseudo_tetrisio.value}\n"
            f"Riot ID: {self.id_riot.value}"
        )
        await envoyer_log(self.bot, interaction.user, "Soumission Partie 1", "INFO", f"Données reçues, écriture GSheets...\n\n{details}")
        
        try:
            data = {
                "Smite 2": self.pseudo_smite2.value,
                "Legion TD 2": self.pseudo_legiontd2.value,
                "Tetris.io": self.pseudo_tetrisio.value,
                "Riot ID": self.id_riot.value
            }
            await asyncio.to_thread(update_or_insert_player, interaction.user.id, interaction.user.name, data)
            
            await envoyer_log(self.bot, interaction.user, "Succès Partie 1", "SUCCES", "Partie 1 correctement injectée dans le GSheets.")
            
            await interaction.followup.send(
                content="✅ **Partie 1 enregistrée !** Clique ci-dessous pour passer à la suite :", 
                view=ActionEtapeSuivante(prochaine_etape=2, bot=self.bot), 
                ephemeral=True
            )
        except Exception as e:
            await envoyer_log(self.bot, interaction.user, "Erreur Partie 1", "ERREUR", f"Crash écriture GSheets :\n{e}")
            await interaction.followup.send(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)


class ModalJeux2(discord.ui.Modal, title="Partie 2 : Vos Pseudos"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck", style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches", style=discord.TextStyle.short)
    pseudo_ohbabykart = discord.ui.TextInput(label="Pseudo Oh Baby Kart", style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="Pseudo Supercell ID (Brawl Stars)", style=discord.TextStyle.short, placeholder="MonPseudo")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        details = (
            f"Puck: {self.pseudo_puck.value}\n"
            f"A few quick matches: {self.pseudo_afewquickmatches.value}\n"
            f"Oh Baby Kart: {self.pseudo_ohbabykart.value}\n"
            f"Brawl Stars: {self.id_brawlstars.value}"
        )
        await envoyer_log(self.bot, interaction.user, "Soumission Partie 2", "INFO", f"Données reçues, écriture GSheets...\n\n{details}")
        
        try:
            data = {
                "Puck": self.pseudo_puck.value,
                "A few quick matches": self.pseudo_afewquickmatches.value,
                "Oh Baby Kart": self.pseudo_ohbabykart.value,
                "Brawl Stars": self.id_brawlstars.value
            }
            await asyncio.to_thread(update_or_insert_player, interaction.user.id, interaction.user.name, data)
            
            await envoyer_log(self.bot, interaction.user, "Succès Partie 2", "SUCCES", "Partie 2 correctement mise à jour dans le GSheets.")
            
            await interaction.followup.send(
                content="✅ **Partie 2 enregistrée !** Clique ci-dessous pour donner ton profil :", 
                view=ActionEtapeSuivante(prochaine_etape=3, bot=self.bot), 
                ephemeral=True
            )
        except Exception as e:
            await envoyer_log(self.bot, interaction.user, "Erreur Partie 2", "ERREUR", f"Crash écriture GSheets :\n{e}")
            await interaction.followup.send(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)


class ModalProfil(discord.ui.Modal, title="Partie 3 : Votre Profil"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    meilleurs_jeux = discord.ui.TextInput(label="Ton meilleur jeu", style=discord.TextStyle.short, placeholder="Tetris.io, Smite 2, ...")
    pire_jeux = discord.ui.TextInput(label="Ton pire jeu", style=discord.TextStyle.short, placeholder="Oh Baby Kart, ...")
    remarques = discord.ui.TextInput(label="Remarques", style=discord.TextStyle.long, placeholder="Quelque chose à ajouter ?", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        details = (
            f"Meilleur Jeu: {self.meilleurs_jeux.value}\n"
            f"Pire Jeu: {self.pire_jeux.value}\n"
            f"Remarques: {self.remarques.value if self.remarques.value else 'Aucune'}"
        )
        await envoyer_log(self.bot, interaction.user, "Soumission Partie 3", "INFO", f"Dernières données reçues, écriture GSheets...\n\n{details}")
        
        try:
            data = {
                "Meilleur Jeu": self.meilleurs_jeux.value,
                "Pire Jeu": self.pire_jeux.value,
                "Remarques": self.remarques.value
            }
            await asyncio.to_thread(update_or_insert_player, interaction.user.id, interaction.user.name, data)
            
            # 🔥 LOG FINAL D'INSCRIPTION COMPLÈTE
            await envoyer_log(self.bot, interaction.user, "INSCRIPTION TERMINÉE 🏆", "SUCCES", "Le joueur a terminé l'intégralité du processus avec succès !")
            
            await interaction.followup.send(
                content=f"🏆 **Inscription validée !**\n\nMerci, toutes tes informations ont été liées à ton compte Discord (**{interaction.user.name}**).",
                ephemeral=True
            )
        except Exception as e:
            await envoyer_log(self.bot, interaction.user, "Erreur Partie 3", "ERREUR", f"Crash écriture GSheets :\n{e}")
            await interaction.followup.send(f"❌ Erreur d'écriture Sheets : {e}", ephemeral=True)

# ==========================================
# 3. LE GROS BOUTON UNIQUE ET PERSISTANT
# ==========================================

class InscriptionView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="S'inscrire 🏆", style=discord.ButtonStyle.green, custom_id="btn_inscription_unique")
    async def bouton_inscription(self, interaction: discord.Interaction, button: discord.ui.Button):
        await envoyer_log(self.bot, interaction.user, "Clic 'S'inscrire'", "INFO", "Lancement du processus. Ouverture de la Partie 1 (ModalJeux1)")
        await interaction.response.send_modal(ModalJeux1(self.bot))

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
        # On passe self.bot à InscriptionView pour qu'elle