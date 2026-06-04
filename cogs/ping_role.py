import discord
from discord.ext import commands
from discord import app_commands

# ✅ LISTE DES IDS AUTORISÉS (Déplacée en haut pour être accessible par la fonction d'autocomplétion)
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

# 🔍 FONCTION D'AUTOCOMPLÉTION
async def roles_autocompletion(interaction: discord.Interaction, current: str):
    """Filtre et ne propose que les rôles présents dans la whitelist."""
    choix = []
    for role_id in ROLES_AUTORISES_IDS:
        role = interaction.guild.get_role(role_id)
        if role:
            # Si l'utilisateur commence à taper du texte, on filtre aussi par le nom
            if current.lower() in role.name.lower():
                # On ajoute le choix (Nom affiché dans Discord, Valeur envoyée au code : l'ID sous forme de string)
                choix.append(app_commands.Choice(name=role.name, value=str(role.id)))
    
    # Discord autorise maximum 25 propositions dans le menu déroulant
    return choix[:25]


class PingRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping_role", description="Mentionne un rôle spécifique")
    @app_commands.describe(role="Le rôle que tu souhaites mentionner")
    @app_commands.autocomplete(role=roles_autocompletion) # 🔥 On lie l'autocomplétion à l'argument "role"
    async def ping_role(self, interaction: discord.Interaction, role: str): # ⚠️ Attention : 'role' devient un 'str' (l'ID reçu de l'autocomplétion)
        
        # 🆔 ID DU RÔLE VISITEUR
        ID_ROLE_VISITEUR = 1508748306216390716  # Rôle 👕| Visiteurs

        # 1. On vérifie si l'utilisateur a le rôle requis
        has_role = any(r.id == ID_ROLE_VISITEUR for r in interaction.user.roles)

        if not has_role:
            await interaction.response.send_message(
                "❌ Désolé, tu dois avoir le rôle `Visiteurs` pour utiliser cette commande !", 
                ephemeral=True
            )
            return

        # 2. On convertit l'ID reçu en véritable objet de rôle Discord
        try:
            role_obj = interaction.guild.get_role(int(role))
            if not role_obj:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "🛑 **Erreur :** Rôle introuvable. Utilise bien les propositions du menu déroulant.", 
                ephemeral=True
            )
            return

        # 3. Double sécurité au cas où (même si l'autocomplétion filtre déjà)
        if role_obj.id not in ROLES_AUTORISES_IDS:
            await interaction.response.send_message(
                f"🛑 **Action refusée :** Le rôle `{role_obj.name}` n'est pas autorisé à être mentionné.", 
                ephemeral=True
            )
            return

        # 4. Si c'est bon, on lance la procédure de ping
        await interaction.response.send_message(f"🔄 Préparation de la mention pour {role_obj.name}...", ephemeral=True)

        try:
            # 5. On ouvre temporairement le rôle s'il est verrouillé
            deja_mentionnable = role_obj.mentionable
            if not deja_mentionnable:
                await role_obj.edit(mentionable=True, reason="Ping sécurisé via commande bot")

            # 6. On envoie le ping dans le salon
            await interaction.channel.send(f"**{role_obj.mention}**")

            # 7. On referme le rôle direct
            if not deja_mentionnable:
                await role_obj.edit(mentionable=False, reason="Verrouillage de sécurité après ping")

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Erreur : Je n'ai pas la permission de modifier ou de mentionner ce rôle. Vérifie que mon rôle est bien tout en haut de la liste dans les paramètres du serveur.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PingRole(bot))