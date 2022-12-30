
import logging
import interactions
from utils.db import DB
from utils.chartCreator import ChartCreator

class StatsCreator():

    def __init__(self, db:DB, chartCreator:ChartCreator):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._db:DB = db
        self._chartCreator:ChartCreator = chartCreator

    def getStatsContent(self, playerName:str):
        playerData = self._db.getPlayerData(playerName)
        if not playerData:
            return False
        
        playerStats = self._db.getPlayerStats(playerData[1])
        allianceData = self._db.getAllianceById(playerData[5])

        currentPlayerStats = playerStats[0]

        currentPlayerStats = self._getCurrentPlayerStats(playerStats[0])
        diffData = self._getStatsDifference(playerStats)


        #Embed Fields
        statsFields = [
            interactions.EmbedField(
                inline=True,
                name="Type",
                value="Gesamt\nGebäude\nForschung\nFlotte\nVerteidigung\n"
            ),
            interactions.EmbedField(
                inline=True,
                name="Rang",
                value= self._getEmbedValueString(currentPlayerStats[0], diffData[0])
            ),
            interactions.EmbedField(
                inline=True,
                name="Punkte",
                value= self._getEmbedValueString(currentPlayerStats[1], diffData[1])
            )
        ]

        #Add Planet Data
        statsFields += self._getPlanetFields(playerData[1])

        #Add Research Data
        statsFields += self._getResearchFields(playerData[1])

        #Create Embed
        statsEmbed = interactions.Embed(
            title=f"{playerData[2]}",
            description= f"{playerData[1]}\n{allianceData[2]}", #PlayerId and Alliance Name
            fields = statsFields,
            timestamp=playerStats[0][19],
            thumbnail=interactions.EmbedImageStruct(
                url=self._chartCreator.getChartUrl(playerStats,playerData[2]),
                height=720,
                width=420
            )
        )

        statsComponents = [
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label='Planet Hinzufügen',
                custom_id='btn_planet'
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label='Forschung ändern',
                custom_id='btn_research'
            ),
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label='Allianz',
                custom_id='btn_alliance'
            ),
            interactions.Button(
                style=interactions.ButtonStyle.SUCCESS,
                label='Aktualisieren',
                custom_id='btn_reload'
            ),
        ]
        
        return (statsEmbed, statsComponents)


    def _getPlanetFields(self, playerId:str):
        planetData = self._db.getPlayerPlanets(playerId)

        planetEmbeds = [
            interactions.EmbedField(
                name="Position",
                value="",
                inline=True
            ),
            interactions.EmbedField(
                name="Mond",
                value="",
                inline=True
            ),
            interactions.EmbedField(
                name="Sensor Phalanx",
                value="",
                inline=True
            ),
        ]

        planetData.sort(key=lambda element: (element[2], element[3], element[4]))
        for planet in planetData:
            planetEmbeds[0].value += f"{planet[2]}\:{planet[3]}\:{planet[4]}\n"
            
            value = "-"
            if planet[5]:
                value = ":ballot_box_with_check:"
            planetEmbeds[1].value += f"{value}\n"

            value = "-"
            if planet[5] and planet[6] >=0:
                value = planet[6]
            planetEmbeds[2].value += f"{value}\n"
        
        if not planetData:
            planetEmbeds[0].value = "-"
            planetEmbeds[1].value = "-"
            planetEmbeds[2].value = "-"

        return planetEmbeds

    def _getResearchFields(self, playerId:str):

        researchData = self._db.getResearch(playerId)

        if not researchData:
            researchData = [0,0,'-','-','-','Kein Eintrag']

        researchFields= [
            interactions.EmbedField(
                inline=True,
                name="Forschung",
                value="Waffentechnik\nSchildtechnik\nRaumschiffpanzerung"
            ),
            interactions.EmbedField(
                inline=True,
                name="Level",
                value=f"{researchData[2]}\n{researchData[3]}\n{researchData[4]}"
            ),
            interactions.EmbedField(
                inline=True,
                name="Letze Forschungs änderung: ",
                value=f"{researchData[5]}"
            )
        ]

        return researchFields

    def _getEmbedValueString(self, data, diff):
        #get largest number
        maxLenghtData = len(max(data, key=len))

        result = "`"

        for elementData,elementDiff in zip(data,diff):
            result += elementData.ljust(maxLenghtData) + " " + elementDiff + "\n"

        return result + "`"

    def _getCurrentPlayerStats(self, playerStats):
        currentRank = [
            self.formatNumber(playerStats[1]),
            self.formatNumber(playerStats[5]),
            self.formatNumber(playerStats[3]),
            self.formatNumber(playerStats[9]),
            self.formatNumber(playerStats[7]),
        ]

        currentScore = [
            self.formatNumber(playerStats[2]),
            self.formatNumber(playerStats[6]),
            self.formatNumber(playerStats[4]),
            self.formatNumber(playerStats[10]),
            self.formatNumber(playerStats[8]),
        ]
        return [currentRank, currentScore]

    def _getStatsDifference(self, playerStats):
        if len(playerStats) == 1:
            return [ 
                ["n/a","n/a","n/a","n/a","n/a"],
                ["n/a","n/a","n/a","n/a","n/a",]
            ]

        current = playerStats[0]
        last= playerStats[1]
            
        diffRank = [
            self._formatDiff(int(current[1])-int(last[1])),
            self._formatDiff(int(current[5])-int(last[5])),
            self._formatDiff(int(current[3])-int(last[3])),
            self._formatDiff(int(current[9])-int(last[9])),
            self._formatDiff(int(current[7])-int(last[7]))
        ]

        diffStats = [
            self._formatDiff(int(current[2])-int(last[2])),
            self._formatDiff(int(current[6])-int(last[6])),
            self._formatDiff(int(current[4])-int(last[4])),
            self._formatDiff(int(current[10])-int(last[10])),
            self._formatDiff(int(current[8])-int(last[8]))
        ]

        return [diffRank, diffStats]

    def _formatDiff(self, number):
        return f"({number:+,})".replace(",",".")

    def formatNumber(self, number):
        return f"{number:,}".replace(",",".")