import discord
import string

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