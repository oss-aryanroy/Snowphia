import config
import discord
from typing import Optional
from discord.ext import commands
from urllib.parse import quote_plus

class SpotifyButton(discord.ui.View):
    def __init__(self, ctx: commands.Context, act: discord.Spotify, *, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.add_item(discord.ui.Button(label='Listen On Spotify', url=act.track_url, emoji="<:Spotify:919727284066336789>"))
        self.act = act
        self.context = ctx
        self.author = ctx.author
	
    async def on_timeout(self):
        for view in self.children:
            view.disabled = True
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.author:
            return True
        else:
            em = discord.Embed(title="Begone!", description=f"This is not yours, only **`{self.author.name}`** can use this button.")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return False

    @discord.ui.button(emoji="<:trashcan:919732033222246440>", label="Close Embed", style=discord.ButtonStyle.red)
    async def deletembed(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()


class ButtonDelete(discord.ui.View):
    __slors__ = ('context')
    def __init__(self,ctx):
        super().__init__(timeout=60)
        self.context = ctx
    async def on_timeout(self):
        self.clear_items()
        #await self.message.edit(view=self)
        self.stop()
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.context.author.id:
            return True
        checkmbed = discord.Embed(
            colour=0x2F3136,
            description=f"Oi! <@{interaction.user.id}>, Only <@{self.context.author.id}> can use this.",
            timestamp=self.context.message.created_at
        )
        await interaction.response.send_message(embed=checkmbed, ephemeral=True)
        return False
    @discord.ui.button(emoji='<:Trashcan:919192387052535869>', style=discord.ButtonStyle.gray)
    async def buttondelete(self, button: discord.ui.Button, interaction: discord.Interaction):
            await self.context.message.add_reaction("<:GreenTick:919192513611431946>")
            await interaction.message.delete()
    