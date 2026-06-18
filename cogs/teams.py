import discord
from discord.ext import commands
from discord import app_commands

class Teams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.team_roles = [
                1517086623160864868,1517086669092950126,1517086682053214269,1517086700122406932,1517086712331763802,
                1517086724004647056,1517086724004647056,1517086736428171274,1517086749342433280,1517086763070521454,
                1517086842418237570,1517086856259571822
            ]
    
    @app_commands.command(name="set_team", description="Attribue une équipe à des joueurs")
    @app_commands.describe(
        equipe="Le rôle de l'équipe à donner",
        joueur1="Le premier joueur",
        joueur2="Le deuxième joueur (optionnel)"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(equipe=[
        app_commands.Choice(name="Team A", value="1517086623160864868"),
        app_commands.Choice(name="Team B", value="1517086669092950126"),
        app_commands.Choice(name="Team C", value="1517086682053214269"),
        app_commands.Choice(name="Team D", value="1517086700122406932"),
        app_commands.Choice(name="Team E", value="1517086712331763802"),
        app_commands.Choice(name="Team F", value="1517086724004647056"),
        app_commands.Choice(name="Team G", value="1517086724004647056"),
        app_commands.Choice(name="Team H", value="1517086736428171274"),
        app_commands.Choice(name="Team I", value="1517086749342433280"),
        app_commands.Choice(name="Team J", value="1517086763070521454"),
        app_commands.Choice(name="Team K", value="1517086842418237570"),
        app_commands.Choice(name="Team L", value="1517086856259571822"),
    ])

    async def set_team(self, interaction: discord.Interaction, equipe: app_commands.Choice[str], joueur1: discord.Member, joueur2: discord.Member = None):
        liste_joueurs = []
        if joueur1 is not None:
            liste_joueurs.append(joueur1)
        if joueur2 is not None:
            liste_joueurs.append(joueur2)

        await interaction.response.defer(ephemeral=True)

        if len(liste_joueurs) > 0:
            for joueur in liste_joueurs:
                for roles_joueur in joueur.roles:
                    if roles_joueur.id in self.team_roles:
                        await joueur.remove_roles(roles_joueur)

        id_role = int(equipe.value)
        role = interaction.guild.get_role(id_role)
        for joueur in liste_joueurs:
            await joueur.add_roles(role)
        
        await interaction.followup.send(f"✅ L'équipe {role.name} a bien été attribuée !", ephemeral=True)

    @app_commands.command(name="loose", description="Envoie des joueurs en Loser Bracket (avec ou sans équipe)")
    @app_commands.describe(
        role_team_loser="Le rôle d'équipe de Loser à leur attribuer (Optionnel pour la Phase 1)",
        j1="Premier joueur",
        j2="Deuxième joueur (optionnel)",
        j3="Troisième joueur (optionnel)",
        j4="Quatrième joueur (optionnel)"
    )
    @app_commands.default_permissions(administrator=True)
    async def loose(
        self, 
        interaction: discord.Interaction, 
        j1: discord.Member, 
        role_team_loser: discord.Role = None,  # <-- Mis en optionnel ici et placé après j1
        j2: discord.Member = None, 
        j3: discord.Member = None, 
        j4: discord.Member = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        # Récupération des rôles généraux (remplace par tes vrais IDs)
        role_winner = interaction.guild.get_role(123456789012345678)
        role_loser = interaction.guild.get_role(987654321098765432)
        
        liste_joueurs = [j for j in [j1, j2, j3, j4] if j is not None]
        pseudos_modifies = []

        for joueur in liste_joueurs:
            # 1. On retire le rôle Winner Bracket
            if role_winner in joueur.roles:
                await joueur.remove_roles(role_winner)
                
            # 2. On ajoute le rôle Loser Bracket
            if role_loser not in joueur.roles:
                await joueur.add_roles(role_loser)
                
            # 3. On ajoute le rôle d'équipe UNIQUEMENT s'il a été renseigné
            if role_team_loser is not None and role_team_loser not in joueur.roles:
                await joueur.add_roles(role_team_loser)
                
            pseudos_modifies.append(joueur.display_name)
            
        membres_str = ", ".join(pseudos_modifies)
        
        # Message de fin dynamique selon si on a mis une équipe ou pas
        if role_team_loser:
            msg = f"💀 {membres_str} ont été envoyés en **Loser Bracket** dans l'équipe **{role_team_loser.name}** !"
        else:
            msg = f"💀 {membres_str} ont été envoyés en **Loser Bracket** (Mode Solo) !"
            
        await interaction.followup.send(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Teams(bot))