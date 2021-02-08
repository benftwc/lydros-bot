from .base_command import BaseCommand


# This show an invite link to this bot
class Scan(BaseCommand):
    def __init__(self):
        description = (
            "Scan character. Usage `!scan <nickname*> <realm:hyjal> <region:eu>`"
        )
        params = ["nickname", ("realm", "hyjal"), ("region", "eu")]
        super().__init__(description, params)

    async def handle(self, params, message, client):
        print(message)
        print(params)
        try:
            nickname = params[0].lower()

            try:
                realm = str(params[1]).lower()
            except IndexError:
                realm = self.params[1][1]

            try:
                region = str(params[2]).lower()
            except IndexError:
                region = self.params[2][1]
        except ValueError:
            await client.send_message(message.channel, "Nickname is missing")
            return

        await message.channel.send(
            f"https://raider.io/characters/{region}/{realm}/{nickname}"
        )
