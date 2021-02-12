import datetime
import time

from .base_command import BaseCommand

start_time = time.time()

# This show an invite link to this bot
class Uptime(BaseCommand):
    def __init__(self):
        description = "Get this bot Uptime !"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime = str(datetime.timedelta(seconds=difference))

        await message.channel.send(f"Uptime is : {uptime}")
