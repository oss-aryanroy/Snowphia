import discord
from typing import Optional
from discord.ext import commands
from utils.context import CustomContext



class SpotifyButton(discord.ui.View):
    def __init__(self, ctx: commands.Context, act: discord.Spotify, *, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.add_item(
            discord.ui.Button(label='Listen On Spotify', url=act.track_url, emoji="<:Spotify:919727284066336789>"))
        self.act = act
        self.context = ctx
        self.author = ctx.author

    async def on_timeout(self):
        self.deletembed.disabled = True
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.author:
            return True
        else:
            em = discord.Embed(title="Begone!",
                               description=f"This is not yours, only **`{self.author.name}`** can use this button.")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return False

    @discord.ui.button(emoji="<:trashcan:919732033222246440>", label="Close Embed", style=discord.ButtonStyle.red)
    async def deletembed(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()


class ButtonDelete(discord.ui.View):
    __slots__ = ('context',)

    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.context = ctx

    async def on_timeout(self):
        self.clear_items()
        # await self.message.edit(view=self)
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

class PrefixConfirm(discord.ui.View):
    def __init__(self, ctx: CustomContext, prefix: str, *, timeout: Optional[float] = 180):
        super().__init__(timeout=timeout)
        self.prefix = prefix
        self.context = ctx

    async def on_timeout(self):
        self.confirm.disabled = True
        self.abort.disabled = True
        await self.message.edit(view=self)

    async def disable_all(self, content: str):
        self.confirm.disabled = True
        self.abort.disabled = True
        try:
            await self.message.edit(content=content, view=self, 
                                    allowed_mentions=discord.AllowedMentions.none())
        except (discord.NotFound, discord.HTTPException):
            pass
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.context.author:
            return True
        else:
            em = discord.Embed(title="Begone!",
                               description=f"This is not yours, only **`{self.context.author.name}`** can use this button.")
            await interaction.response.send_message(embed=em, ephemeral=True)
            return False
            
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        args = """INSERT INTO guild_info(guild_id, prefix)
                  VALUES ($1, $2)
                  ON CONFLICT(guild_id)
                  DO UPDATE SET prefix = $2"""
        await self.context.db.execute(args, self.context.guild.id, self.prefix)
        prefix = self.prefix if self.prefix else 'sn!'
        self.context.bot.update_cache(self.context.guild, self.prefix)
        await self.disable_all(f'Your prefix has been successfully set to `{prefix}`')
        

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def abort(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.disable_all('Aborting setting a new prefx...')
