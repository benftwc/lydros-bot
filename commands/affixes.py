from discord import Embed, Colour
from .base_command import BaseCommand
import requests
import json
from io import BytesIO

# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Affixes(BaseCommand):
    def __init__(self):
        description = "Displays current affixes."
        params = [("region", "eu")]
        super().__init__(description, params)

    async def handle(self, params, message, client):

        try:
            region = str(params[0]).lower()
        except IndexError:
            region = self.params[0][1]

        response = requests.get(f"https://mythicpl.us/affix-{region}")
        affixesData = json.loads(response.content)

        embed = Embed(
            title=f"What to deal with in the {region.upper()} ? (clic for leaderboard)",
            url=affixesData["leaderboard_url"],
            description=affixesData["title"],
        )
        for affix in affixesData["affix_details"]:
            embed.add_field(
                name=affix["name"], value=affix["description"], inline=False
            )

        await message.channel.send(embed=embed)
