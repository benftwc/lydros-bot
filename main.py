import sentry_sdk

sentry_sdk.init(
    "https://d823f9bc28134dd9b57f9e41b86f953c@o472921.ingest.sentry.io/5627038",
    traces_sample_rate=1.0,
)

import sys

import settings
import discord
import message_handler
import re
import asyncio
from datetime import date

from discord import Embed
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from events.base_event import BaseEvent
from events import *
from multiprocessing import Process

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()


###############################################################################


def main():
    print("Warming up...")
    client = discord.Client()

    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        if settings.NOW_PLAYING:
            print("Setting NP game", flush=True)
            await client.change_presence(
                activity=discord.Game(name=settings.NOW_PLAYING)
            )
        print("Logged in!", flush=True)

        # Load all events
        print("Loading events...", flush=True)
        n_ev = 0
        for ev in BaseEvent.__subclasses__():
            event = ev()
            sched.add_job(
                event.run, "interval", (client,), minutes=event.interval_minutes
            )
            n_ev += 1
        sched.start()
        print(f"{n_ev} events loaded", flush=True)

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        if text.startswith(settings.COMMAND_PREFIX) and text != settings.COMMAND_PREFIX:
            cmd_split = text[len(settings.COMMAND_PREFIX) :].split()
            try:
                await message_handler.handle_command(
                    cmd_split[0].lower(), cmd_split[1:], message, client
                )
            except:
                print("Error while handling message", flush=True)
                raise

    @client.event
    async def on_message(message):
        warcraftlogs_pattern = re.compile(settings.WARCRAFTLOGS_REGEX)
        if warcraftlogs_pattern.search(message.content):
            channel = message.channel
            logUrl = message.content

            firstPromptBot = await channel.send("Log de raid ?")
            await firstPromptBot.add_reaction("👍")
            await firstPromptBot.add_reaction("👎")

            def checkReact(reaction, user):
                return user == message.author and str(reaction.emoji) in ["👍", "👎"]

            def checkAuthorID(user):
                return user.author.id == message.author.id

            try:
                reaction, user = await client.wait_for(
                    "reaction_add", timeout=10.0, check=checkReact
                )
            except asyncio.TimeoutError:
                await firstPromptBot.delete()
            else:
                await firstPromptBot.delete()
                # await message.add_reaction("👌")
                await message.add_reaction("<:lydros:816500068009377803>")
                if reaction.emoji == "👍":
                    await message.delete()
                    secondPromptBot = await channel.send("Titre du log ?")
                    try:
                        logNameMessage = await client.wait_for(
                            "message", check=checkAuthorID
                        )
                    except asyncio.TimeoutError:
                        await firstPromptBot.delete()
                    else:
                        await secondPromptBot.delete()
                        await logNameMessage.delete()
                        now = date.today()
                        embed = Embed(
                            title=f"{now.strftime('%d/%m/%Y')} ** {logNameMessage.content} ** from @{user.name}",
                            url=logUrl,
                        )
                        embed.add_field(name="Warlogs", value=logUrl, inline=False)
                        embed.add_field(name="Warlogs", value=logUrl, inline=False)
                        embed.add_field(name="Warlogs", value=logUrl, inline=False)
                        embed.add_field(name="Warlogs", value=logUrl, inline=False)

                        await message.channel.send(embed=embed)
        await common_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    # Finally, set the bot running
    client.run(settings.BOT_TOKEN)


###############################################################################


if __name__ == "__main__":
    main()
