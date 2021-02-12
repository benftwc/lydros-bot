import json
import logging

import requests
from discord import Embed

from .base_command import BaseCommand

# This show an invite link to this bot
class Scan(BaseCommand):
    def __init__(self):
        description = (
            "Scan character. Usage `!scan <nickname*> <realm:hyjal> <region:eu>`"
        )
        params = ["nickname", ("realm", "Hyjal"), ("region", "eu")]
        super().__init__(description, params)

    @staticmethod
    def get_api_fields():
        return f"raid_progression,mythic_plus_ranks,mythic_plus_best_runs,gear,mythic_plus_scores"

    @staticmethod
    def get_raid_order():
        return [
            "the-eternal-palace",
            "crucible-of-storms",
            "battle-of-dazaralor",
            "uldir",
            "nyalotha-the-waking-city",
            "castle-nathria",
        ]

    @staticmethod
    def get_raid_shortnames(raidname):
        raids = {
            "the-eternal-palace": "EP",
            "crucible-of-storms": "CoS",
            "battle-of-dazaralor": "BoD",
            "uldir": "Uldir",
            "nyalotha-the-waking-city": "NYA",
            "castle-nathria": "CN",
        }

        return raids[raidname] or raidname

    @staticmethod
    def get_class_colours(userClass):
        classColor = {
            "Warrior": 0xC79C6E,  # #c79c6e
            "Warlock": 0x9482C9,  # #9482c9
            "Shaman": 0x0070DE,  # #0070de
            "Rogue": 0xFFF569,  # #fff569
            "Priest": 0xFFFFFF,  # #ffffff
            "Paladin": 0xF58CBA,  # #f58cba
            "Monk": 0x00FF96,  # #00ff96
            "Mage": 0x69CCF0,  # #69ccf0
            "Hunter": 0xABD473,  # #abd473
            "Druid": 0xFF7D0A,  # #ff7d0a
            "Death Knight": 0xC41E3A,  # #C41E3A
            "Demon Hunter": 0xA330C9,  # #A330C9
        }
        try:
            return classColor[userClass]
        except KeyError:
            logging.error(f"SCAN command : {userClass} does not exists in classColors")
            return classColor["Warrior"]

    @staticmethod
    def get_character_ranking(rankings, rankType, rankPool="realm"):
        trueRankType = f"faction_class_{rankType}"
        if trueRankType not in rankings:
            return "NA"
        return rankings[trueRankType][rankPool]

    async def handle(self, params, message, client):
        try:
            nickname = params[0].lower()

            try:
                realm = str(params[1]).capitalize()
            except IndexError:
                realm = self.params[1][1]

            try:
                region = str(params[2]).lower()
            except IndexError:
                region = self.params[2][1]
        except ValueError:
            await client.send_message(message.channel, "Nickname is missing")
            return

        try:
            response = requests.get(
                f"https://raider.io/api/v1/characters/profile?region={region}&realm={realm}&name={nickname}&fields={self.get_api_fields()}"
            )

            character = json.loads(response.content)

            if not "name" in character:
                await message.channel.send(
                    f"{nickname}-{realm} [{region.upper()}] is not found on raider.io, please check spelling :face_with_monocle: or add informations such as realm or region.",
                )
                return

            progress = character["raid_progression"] or []
            userProgress = []

            for raid in self.get_raid_order():
                if raid in progress:
                    nm_score = int(progress[raid]["normal_bosses_killed"]) or 0
                    hm_score = int(progress[raid]["heroic_bosses_killed"]) or 0
                    mm_score = int(progress[raid]["mythic_bosses_killed"]) or 0

                    if nm_score + hm_score + mm_score != 0:
                        userProgress.append(
                            f"{self.get_raid_shortnames(raid)} - {progress[raid]['summary']}"
                        )

            if not len(userProgress):
                userProgress.append("No progress for current patch")

            bestRuns = character["mythic_plus_best_runs"]
            bestRunOutput = []

            if len(bestRuns):
                bestRunOutput.append(
                    f"{bestRuns[0]['short_name']} {bestRuns[0]['mythic_level']} {'*' * bestRuns[0]['num_keystone_upgrades']}"
                )
                bestRunOutput.append(
                    f"{bestRuns[1]['short_name']} {bestRuns[1]['mythic_level']} {'*' * bestRuns[1]['num_keystone_upgrades']}"
                )
                bestRunOutput.append(
                    f"{bestRuns[2]['short_name']} {bestRuns[2]['mythic_level']} {'*' * bestRuns[2]['num_keystone_upgrades']}"
                )
            else:
                bestRunOutput.append("No recent mythic+ runs.")

            userRealmRankings = character["mythic_plus_ranks"]
            userParsedRanks = {"tank": "NA", "healer": "NA", "dps": "NA"}
            roles = {"tank", "healer", "dps"}
            for role in roles:
                userParsedRanks[role] = self.get_character_ranking(
                    userRealmRankings, role
                )

            realmRankingsText = f"Tank {userParsedRanks['tank']} - Healer {userParsedRanks['healer']} - DPS {userParsedRanks['dps']}"

            embed = Embed(
                title=f"{character['name']}-{realm}",
                url=f"https://raider.io/characters/{region}/{realm}/{nickname}",
                color=self.get_class_colours(character["class"]),
                description=f"{character['race']} - {character['class']} {character['active_spec_name']} ({character['active_spec_role']})",
            )

            embed.add_field(
                name="Ilevel",
                value=character["gear"]["item_level_equipped"],
                inline=True,
            )

            embed.add_field(
                name="RIO", value=character["mythic_plus_scores"]["all"], inline=True
            )

            embed.add_field(
                name="Achievement points",
                value=character["achievement_points"],
                inline=True,
            )

            embed.add_field(
                name="====================================",
                value="BEST MYTHIC KEYSTONES",
                inline=False,
            )

            if len(bestRunOutput) > 1:
                embed.add_field(name="#1", value=bestRunOutput[0], inline=True)
                embed.add_field(name="#2", value=bestRunOutput[1], inline=True)
                embed.add_field(name="#3", value=bestRunOutput[2], inline=True)
            else:
                embed.add_field(name="#0", value=bestRunOutput[0], inline=True)

            embed.add_field(
                name="====================================", value="RAIDS", inline=False
            )

            embed.add_field(name="Progress", value=userProgress[0], inline=True)

            embed.add_field(name="Ranking", value=realmRankingsText, inline=False)

            embed.add_field(
                name="====================================",
                value="QUICK LINKS",
                inline=False,
            )

            embed.add_field(
                name=":shield: Armory",
                value=f"[Open Armory](https://worldofwarcraft.com/fr-fr/character/{realm}/{nickname})",
                inline=True,
            )

            embed.add_field(
                name=":gear: Armory",
                value=f"[Open raider.io](https://raider.io/characters/{region.lower()}/{realm.lower()}/${nickname})",
                inline=True,
            )

            embed.add_field(
                name=":crossed_swords: Wipefest",
                value=f"[Open Wipefest](https://www.wipefest.net/character/{nickname}/{realm}/{region})",
                inline=True,
            )

            await message.channel.send(embed=embed)
        except requests.exceptions.ConnectionError as err:
            logging.error(err)
            await message.channel.send(
                f"raider.io API ERROR, please contact support if many attempts fail."
            )
            return
