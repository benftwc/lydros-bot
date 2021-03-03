import os

from decouple import config

# The prefix that will be used to parse commands.
# It doesn't have to be a single character!
COMMAND_PREFIX = config("BOT_DEFAULT_PREFIX")

# The bot token. Keep this secret!
BOT_TOKEN = config("DISCORD_API_BOT_TOKEN")
BOT_CLIENT_ID = config("DISCORD_CLIENT_ID")
# The now playing game. Set this to anything false-y ("", None) to disable it
NOW_PLAYING = COMMAND_PREFIX + "commands"

# Base directory. Feel free to use it if you want.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

WARCRAFTLOGS_REGEX = "(?:http:\/\/|https:\/\/)(?:www.warcraftlogs.)(?:com|fr)(?:\/)(?:reports)(?:\/)(?:(\w)*)(?:\/)"
