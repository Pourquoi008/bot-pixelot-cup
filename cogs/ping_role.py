import discord
from discord.ext import commands
from discord import app_commands

class PingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping_role", description="Mentionne un rôle spécifique")
    @app_commands.describe(role="Le rôle que tu souhaites mentionner")
    async def ping_role(self, interaction: discord.Interaction, role: discord.Role):
        
        # 🏷️ REMPLACE PAR LE NOM EXACT DE TON RÔLE VISITEUR (avec son émoji s'il fait partie du nom)
        # Exemple : "👀 Visiteur" ou "Visiteur"
        NOM_ROLE_VISITEUR = "👕| Visiteurs" 

        # 1. On vérifie si l'utilisateur a le rôle requis
        has_role = any(r.name == NOM_ROLE_VISITEUR for r in interaction.user.roles)

        if not has_role:
            await interaction.response.send_message(
                f"❌ Désolé, tu dois avoir le rôle `{NOM_ROLE_VISITEUR}` pour utiliser cette commande !", 
                ephemeral=True
            )
            return

        # 2. Si c'est bon, on lance la procédure de ping
        await interaction.response.send_message(f"🔄 Préparation de la mention pour {role.name}...", ephemeral=True)

        try:
            # 3. On ouvre temporairement le rôle s'il est verrouillé
            deja_mentionnable = role.mentionable
            if not deja_mentionnable:
                await role.edit(mentionable=True, reason="Ping sécurisé via commande bot")

            # 4. On envoie le ping dans le salon
            await interaction.channel.send(f"**{role.mention}**")

            # 5. On referme le rôle direct
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