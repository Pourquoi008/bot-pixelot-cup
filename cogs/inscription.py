import discord
import string
from discord import app_commands 

class InscriptionModal(discord.ui.Modal,title="Inscription"):
    pseudo_smite2 = discord.ui.TextInput(label="Pseudo Smite 2",style=discord.TextStyle.short)
    pseudo_legiontd2 = discord.ui.TextInput(label="Pseudo Legion TD 2",style=discord.TextStyle.short)
    pseudo_tetrisio = discord.ui.TextInput(label="Pseudo Tetris.io",style=discord.TextStyle.short)
    id_riot = discord.ui.TextInput(label="ID Riot",style=discord.TextStyle.short)
    pseudo_puck = discord.ui.TextInput(label="Pseudo Puck",style=discord.TextStyle.short)
    pseudo_afewquickmatches = discord.ui.TextInput(label="Pseudo A few quick matches",style=discord.TextStyle.short)
    pseudo_ohbabykart =discord.ui.TextInput(label="Pseudo Oh Baby Kart",style=discord.TextStyle.short)
    id_brawlstars = discord.ui.TextInput(label="ID Brawl Stars",style=discord.TextStyle.short)
    meilleurs_jeux =discord.ui.TextInput(label="Ton meilleur jeu",style=discord.TextStyle.short,placeholder="Tetris.io, Smite 2, ...")
    pire_jeux =discord.ui.TextInput(label="Ton pire jeu",style=discord.TextStyle.short,placeholder="Oh Baby Kart, A few quick matches, ...")
    remarques =discord.ui.TextInput(label="Remarques",style=discord.TextStyle.long,placeholder="Si tu as des remarques à faire, c'est ici que ça se passe !")

    async def on_submit(self,interaction:discord.Interaction):
        try:
            if interaction.channel.name!="『🥇』inscription-ranked":
                await interaction.response.send_message("⚠️ Vous n'êtes pas dans le salon d'inscription !",ephemeral=True)
                return
            # On répond au joueur quand il a cliqué sur Envoyer
            await interaction.response.send_message(f"✅ Pseudos enregistrés, merci {interaction.user.mention} !", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)

# 2. C'est ICI qu'on crée le bouton qui va lancer le Modal
class InscriptionView(discord.ui.View):
    def __init__(self):
        # timeout=None est TRÈS important : ça rend le bouton persistant (il ne s'éteint jamais)
        super().__init__(timeout=None) 

    # On définit le bouton vert. Le custom_id est obligatoire pour les boutons persistants
    @discord.ui.button(label="S'inscrire à la Cup", style=discord.ButtonStyle.green, emoji="📝", custom_id="btn_inscription")
    async def bouton_inscription(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        # 🔒 Ta sécurité pour vérifier le salon (Remplace par l'ID de ton salon !)
        # C'est beaucoup plus sûr que le nom du salon
        ID_SALON_INSCRIPTION = 1509961077696237778  
        
        if interaction.channel_id != ID_SALON_INSCRIPTION:
            await interaction.response.send_message("⚠️ Vous n'êtes pas dans le salon d'inscription !", ephemeral=True)
            return

        # 🚀 LA MAGIE : Quand il clique, on lui ouvre le Modal !
        await interaction.response.send_modal(InscriptionModal())


# ==========================================
# 3. LE COG PRINCIPAL (COMMANDE SLASH)
# ==========================================

class Inscription(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. On utilise app_commands au lieu de commands
    @app_commands.command(name="lancer_panneau", description="Affiche le panneau avec les boutons d'inscription")
    # 2. Seuls les membres avec la permission Administrateur peuvent la voir/lancer
    @app_commands.default_permissions(administrator=True)
    async def lancer_panneau(self, interaction: discord.Interaction):
        
        # On valide l'interaction tout de suite en envoyant un message invisible 
        # pour confirmer que la commande a été reçue (obligatoire pour les slash commands)
        await interaction.response.send_message("⌛ Génération du panneau...", ephemeral=True)

        embed = discord.Embed(
            title="🏆 Inscriptions à la Pixelot Cup 2026",
            description=(
                "Prêt à relever le défi ?\n\n"
                "📌 Cliquez sur le bouton ci-dessous pour remplir vos identifiants de jeu et valider votre participation !"
            ),
            color=discord.Color.gold()
        )

        await interaction.channel.send(embed=embed, view=InscriptionView())

async def setup(bot):
    await bot.add_cog(Inscription(bot))