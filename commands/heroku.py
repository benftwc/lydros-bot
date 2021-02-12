import os

from discord import Embed

from .base_command import BaseCommand

# This show an invite link to this bot
class Heroku(BaseCommand):
    def __init__(self):
        description = "Get Heroku instance details !"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        embed = Embed(
            title=f"Details for {os.getenv('HEROKU_SLUG_DESCRIPTION')}",
        )
        herokuMetrics = [
            "HEROKU_APP_ID",
            "HEROKU_APP_NAME",
            "HEROKU_DYNO_ID",
            "HEROKU_RELEASE_CREATED_AT",
            "HEROKU_RELEASE_VERSION",
            "HEROKU_SLUG_COMMIT",
            "HEROKU_SLUG_DESCRIPTION",
        ]
        for metric in herokuMetrics:
            embed.add_field(name=metric, value=os.getenv(metric), inline=False)

        await message.channel.send(embed=embed)
