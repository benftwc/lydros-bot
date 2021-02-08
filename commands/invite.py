from .base_command import BaseCommand


# This show an invite link to this bot
class Invite(BaseCommand):
    def __init__(self):
        description = "Invite this bot to your discord !"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        from message_handler import COMMAND_HANDLERS

        await message.channel.send(
            "https://discord.com/api/oauth2/authorize?client_id=808158954014244906&permissions=29387840&scope=bot"
        )
