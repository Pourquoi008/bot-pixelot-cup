import discord
from discord.ext import commands
from discord import app_commands

class PingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping_role", description="Mentionne un rôle spécifique")
    @app_commands.describe(role="Le rôle que tu souhaites mentionner")
    async def ping_role(self, interaction: discord.Interaction, role: discord.Role):
        
        # 🆔 ID DU RÔLE VISITEUR (Sous forme de NOMBRE, pas de texte)
        ID_ROLE_VISITEUR = 1508748306216390716  # Rôle 👕| Visiteurs

        # ✅ LISTE DES IDS AUTORISÉS (Uniquement des NOMBRES)
        ROLES_AUTORISES = [
            1511991532599775323, # Rôle 🛡️| Legion TD
            1511991679379308574, # Rôle 🟪| Tetr.io
            1511991827115413604, # Rôle 🏒| Puck
            1511991855221571604, # Rôle ⭐| BrawlStars
            1511991896828940428, # Rôle 🎯| Valorant
            1511991917758386227, # Rôle 🏎️| Oh Baby Kart
            1511991987010801705, # Rôle ⚡| Smite 2
            1511992152895524864  # Rôle ⏱️| A few quick match
        ]

        # 1. On vérifie si l'utilisateur a le rôle requis (Vérification par nombre)
        has_role = any(r.id == ID_ROLE_VISITEUR for r in interaction.user.roles)

        if not has_role:
            await interaction.response.send_message(
                "❌ Désolé, tu dois avoir le rôle `Visiteurs` pour utiliser cette commande !", 
                ephemeral=True
            )
            return

        # 2. SÉCURITÉ : Est-ce que l'ID du rôle demandé est bien dans la Whitelist ?
        if role.id not in ROLES_AUTORISES:
            await interaction.response.send_message(
                f"🛑 **Action refusée :** Le rôle `{role.name}` n'est pas autorisé à être mentionné.", 
                ephemeral=True
            )
            return

        # 3. Si c'est bon, on lance la procédure de ping
        await interaction.response.send_message(f"🔄 Préparation de la mention pour {role.name}...", ephemeral=True)

        try:
            # 4. On ouvre temporairement le rôle s'il est verrouillé
            deja_mentionnable = role.mentionable
            if not deja_mentionnable:
                await role.edit(mentionable=True, reason="Ping sécurisé via commande bot")

            # 5. On envoie le ping dans le salon
            await interaction.channel.send(f"**{role.mention}**")

            # 6. On referme le rôle direct
            if not deja_mentionnable:
                await role.edit(mentionable=False, reason="Verrouillage de sécurité après ping")

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Erreur : Je n'ai pas la permission de modifier ou de mentionner ce rôle. Vérifie que mon rôle est bien tout en haut de la liste dans les paramètres du serveur.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PingRole(bot))