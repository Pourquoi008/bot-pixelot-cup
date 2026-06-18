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
    
    ## == /set_team == ##
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
    ## == /loose == ##
    @app_commands.command(name="loose", description="Envoie des joueurs en Loser Bracket (avec ou sans équipe)")
    @app_commands.describe(
        equipe_loser="L'équipe de rechange (Optionnel - Uniquement pour les phases en équipe)",
        j1="Premier joueur",
        j2="Deuxième joueur (optionnel)",
        j3="Troisième joueur (optionnel)",
        j4="Quatrième joueur (optionnel)"
    )
    # 🪄 On limite le choix strictement aux équipes 1, 2, 3, 4, 5, 6 du Loser Bracket
    # Remplace les IDs ci-dessous par les vrais IDs de tes rôles Team Loser
    @app_commands.choices(equipe_loser=[
        app_commands.Choice(name="Team Loser 1", value="1517181231123398906"),
        app_commands.Choice(name="Team Loser 2", value="1517181255337382200"),
        app_commands.Choice(name="Team Loser 3", value="1517181278372237503"),
        app_commands.Choice(name="Team Loser 4", value="1517182710752477327"),
        app_commands.Choice(name="Team Loser 5", value="1517182733665698023"),
        app_commands.Choice(name="Team Loser 6", value="1517181295191392407"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def loose(
        self, 
        interaction: discord.Interaction, 
        j1: discord.Member, 
        equipe_loser: app_commands.Choice[str] = None,  # <-- Devient un choix optionnel
        j2: discord.Member = None, 
        j3: discord.Member = None, 
        j4: discord.Member = None
    ):
        await interaction.response.defer(ephemeral=True)
        
        # Récupération des rôles généraux (Pense à mettre tes vrais IDs ici)
        role_winner = interaction.guild.get_role(1517072565158285443)
        role_loser = interaction.guild.get_role(1517177004976504842)
        
        liste_joueurs = [j for j in [j1, j2, j3, j4] if j is not None]
        pseudos_modifies = []

        for joueur in liste_joueurs:
            # 1. On retire le rôle Winner Bracket
            if role_winner in joueur.roles:
                await joueur.remove_roles(role_winner)
                
            # 2. On ajoute le rôle Loser Bracket
            if role_loser not in joueur.roles:
                await joueur.add_roles(role_loser)
                
            # 3. Si une équipe a été sélectionnée, on va chercher le vrai rôle sur Discord pour l'ajouter
            if equipe_loser is not None:
                id_role = int(equipe_loser.value)
                vrai_role_team = interaction.guild.get_role(id_role)
                
                if vrai_role_team and vrai_role_team not in joueur.roles:
                    await joueur.add_roles(vrai_role_team)
                
            pseudos_modifies.append(joueur.display_name)
            
        membres_str = ", ".join(pseudos_modifies)
        
        # Message de fin adapté
        if equipe_loser:
            msg = f"💀 {membres_str} ont été envoyés en **Loser Bracket** dans la **{equipe_loser.name}** !"
        else:
            msg = f"💀 {membres_str} ont été envoyés en **Loser Bracket** (Solo) !"
            
        await interaction.followup.send(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Teams(bot))