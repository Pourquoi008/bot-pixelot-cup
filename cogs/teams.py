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

async def setup(bot):
    await bot.add_cog(Teams(bot))