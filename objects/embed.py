import discord
from discord.ext import commands
from discord.ui import View, Button
from objects import YTVid

class EmbedMaker:
    def __init__(self, title: str='\u200b', description: str='\u200b', color=0x1a9bd3):
        self.title = title
        self.description = description
        self.color = color

        self.embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )

    def add_field(self, name: str='\u200b', value: str='\u200b', inline: bool=False):
        self.embed.add_field(name=name, value=value, inline=inline)

    def add_thumbnail(self, yt_vid: YTVid):
        self.embed.set_thumbnail(url=yt_vid.thumbnail)

    def add_image(self, image_url: str):
        self.embed.set_image(url=image_url)

    async def send_embed(self, interaction: discord.Interaction, view: View=None, response=False, followup=False):
        # TODO this hurts to look at, clean it
        if followup and view:
            await interaction.followup.send(embed=self.embed, view=view)
        elif response and view:
            await interaction.response.send_message(embed=self.embed, view=view)
        elif response:
            await interaction.response.send_message(embed=self.embed)
        elif view:
            await interaction.channel.send(embed=self.embed, view=view)
        else:
            await interaction.channel.send(embed=self.embed)


    @classmethod
    async def create_text_embed(cls, interaction: discord.Interaction, title: str, description: str, response=False):
        embed = EmbedMaker(title, description)
        await embed.send_embed(interaction, response=response)


    @classmethod
    async def error_response(cls, interaction: discord.Interaction, description: str):
        await EmbedMaker.create_text_embed(interaction, 'Error', description, response=True)


    @classmethod
    async def create_yt_search_embed(cls, interaction: discord.Interaction, bot: commands.Bot, query: str, results: list[YTVid]):
        embed = EmbedMaker(f'Search results for "{query}"', 'Press the corresponding number')
        [embed.add_field(name=f'**{index+1}**) {vid.title}', value=f'By: {vid.channel} ({vid.duration})') for index, vid in enumerate(results)]

        view = View()
        for i in range(len(results)):
            view.add_item(
                Button(
                    style=discord.ButtonStyle.primary,
                    custom_id=str(i),
                    disabled=False,
                    label=str(i+1),
                    row=0
                )
            )
        view.add_item(
            Button(
                style=discord.ButtonStyle.danger,
                custom_id='cancel',
                disabled=False,
                label='Cancel',
                row=1
            )
        )

        await embed.send_embed(interaction, view=view, followup=True)

        selection: discord.Interaction = await bot.wait_for(
            'interaction',
            check=lambda x: x.channel.id == interaction.channel.id
            and x.user.id == interaction.user.id,
            timeout=60.0
        )

        embed2 = EmbedMaker(f'Search results for "{query}"', '**Selection cancelled**')

        if selection.data['custom_id'] == 'cancel':
            await selection.message.edit(embed=embed2.embed, view=None)
            return None

        await selection.message.edit(embed=embed.embed, view=None)
        return results[int(selection.data['custom_id'])]

