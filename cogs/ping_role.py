import discord
from discord.ext import commands
from discord import app_commands

class PingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping_role", description="Mentionne un rôle spécifique (Sécurisé)")
    @app_commands.describe(role="Le rôle autorisé que tu souhaites mentionner")
    async def ping_role(self, interaction: discord.Interaction, role: discord.Role):
        """Commande Slash native : look Discord officiel + sécurité par ID + Logs Console."""
        
        # 🆔 ID DU RÔLE VISITEUR
        ID_ROLE_VISITEUR = 1508748306216390716  # Rôle 👕| Visiteurs

        # ✅ LISTE DES IDS AUTORISÉS (Seuls ces 8 rôles de jeux passeront la sécurité)
        ROLES_AUTORISES_IDS = [
            1511991532599775323, # Rôle 🛡️| Legion TD
            1511991679379308574, # Rôle 🟪| Tetr.io
            1511991827115413604, # Rôle 🏒| Puck
            1511991855221571604, # Rôle ⭐| BrawlStars
            1511991896828940428, # Rôle 🎯| Valorant
            1511991917758386227, # Rôle 🏎️| Oh Baby Kart
            1511991987010801705, # Rôle ⚡| Smite 2
            1511992152895524864  # Rôle ⏱️| A few quick match
        ]

        # --- SÉCURITÉ 1 : Est-ce que l'utilisateur a le rôle Visiteurs ? ---
        has_role = any(r.id == ID_ROLE_VISITEUR for r in interaction.user.roles)

        if not has_role:
            print(f"⚠️ [PING_ROLE] {interaction.user.name} (ID: {interaction.user.id}) a tenté d'utiliser la commande sans le rôle Visiteurs.", flush=True)
            await interaction.response.send_message(
                "❌ Désolé, tu dois avoir le rôle `Visiteurs` pour utiliser cette commande !", 
                ephemeral=True
            )
            return

        # --- SÉCURITÉ 2 : Est-ce que le rôle choisi est dans la Whitelist ? ---
        if role.id not in ROLES_AUTORISES_IDS:
            print(f"🛑 [PING_ROLE] {interaction.user.name} a tenté de pinger un rôle INTERDIT : {role.name} (ID: {role.id}).", flush=True)
            await interaction.response.send_message(
                f"🛑 **Action refusée :** Le rôle `{role.name}` est protégé et ne peut pas être mentionné avec cette commande.", 
                ephemeral=True
            )
            return

        # --- TOUT EST OK : Procédure de ping ---
        print(f"🔄 [PING_ROLE] {interaction.user.name} lance un ping pour le rôle {role.name} dans #{interaction.channel.name}...", flush=True)
        await interaction.response.send_message(f"🔄 Préparation de la mention pour {role.name}...", ephemeral=True)

        try:
            # On ouvre temporairement le rôle s'il est verrouillé dans Discord
            deja_mentionnable = role.mentionable
            if not deja_mentionnable:
                await role.edit(mentionable=True, reason="Ping sécurisé via commande bot")

            # On envoie le ping dans le salon textuel actuel
            await interaction.channel.send(f"**{role.mention}**")
            print(f"✅ [PING_ROLE] Succès : {role.name} a été mentionné par {interaction.user.name}.", flush=True)

            # On reverrouille le rôle juste après le message
            if not deja_mentionnable:
                await role.edit(mentionable=False, reason="Verrouillage de sécurité après ping")

        except discord.Forbidden:
            print(f"❌ [PING_ROLE] Erreur de permissions : Impossible de modifier ou mentionner le rôle {role.name}.", flush=True)
            await interaction.followup.send(
                "❌ Erreur : Je n'ai pas la permission de modifier ou de mentionner ce rôle. Vérifie que mon rôle (Pixelot Cup) est bien tout en haut de la liste dans les paramètres de rôles du serveur.", 
                ephemeral=True
            )
        except Exception as e:
            print(f"❌ [PING_ROLE] Erreur inattendue : {e}", flush=True)
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PingRole(bot))