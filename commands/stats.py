import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.chartMaker import ChartMaker

class Stats(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
        self._chartMaker:ChartMaker = args[2]
    
    @interactions.extension_command(
        name="stats",
        description="Stats des Spielers",
        options = [
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def stats(self, ctx: interactions.CommandContext, username:str = None):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Username: %s", username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        try:
            statsEmbed,statsComponent = self._getStatsContent(username)
        except Exception as e:
            self._logger.warning("Stats content may have an Error")
            self._logger.warning(e)
            await ctx.send(f"{username} nicht gefunden")
            return
        
        await ctx.send(embeds=statsEmbed, components=statsComponent)

    def _getStatsContent(self, playerName:str):
        playerData = self._db.getPlayerData(playerName)
        if not playerData:
            return False
        
        playerStats = self._db.getPlayerStats(playerData[1])
        allianceData = self._db.getAllianceData(playerData[5])


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
                url=self._chartMaker.getChartUrl(playerStats,playerData[2]),
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
        ]
        return (statsEmbed, statsComponents)

    #Planet Modal
    @interactions.extension_component("btn_planet")
    async def modal_planet(self, ctx:interactions.ComponentContext):      
        self._logger.debug("Button clicked: btn_planet from %s", ctx.user.username)

        if not self._auth.check(ctx.user.id, "planet"):
            return
        
        planetModal = interactions.Modal(
            title="Planet Hinzufügen",
            custom_id="modal_planet",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Galaxy",
                    custom_id='planet_gal',
                    placeholder='1-4',
                    required=True,
                    min_length=1,
                    max_length=1,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="System",
                    custom_id='planet_sys',
                    placeholder='1-400',
                    required=True,
                    min_length=1,
                    max_length=3
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Position",
                    custom_id='planet_pos',
                    placeholder='1-15',
                    required=True,
                    min_length=1,
                    max_length=2
                )
            ]
        )
        await ctx.popup(planetModal)

    #Confirm Planet Modal
    @interactions.extension_modal("modal_planet")
    async def modal_planet_save(self, ctx:interactions.ComponentContext, galaxy:str, system:str, position:str):
        self._logger.debug("Modal Confirmed from: %s", ctx.user.username)
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, "planet"):
            return

        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 

        self._db.updatePlanet(playerId, galaxy ,system, position)

        #Workaround get playerName from Title
        statsEmbed,statsButtons = self._getStatsContent(ctx.message.embeds[0].title)

        #edit original message
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        #confirm modal
        await ctx.send()

    #Research Modal
    @interactions.extension_component("btn_research")
    async def modal_research(self, ctx:interactions.ComponentContext):      
        self._logger.debug("Button clicked: btn_research from %s", ctx.user.username)

        if not self._auth.check(ctx.user.id, "research"):
            return
        
        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 
        currentResearch = self._db.getResearch(playerId)

        if not currentResearch:
            currentResearch = [0,0,0,0,0,]

        researchModal = interactions.Modal(
            title="Forschung ändern",
            custom_id="modal_research",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Waffentechnik",
                    custom_id='reasearch_weapon',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[2]
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Schildtechnik",
                    custom_id='reasearch_shield',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[3]
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Raumschiffpanzerung",
                    custom_id='reasearch_armor',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[4]
                )
            ]
        )
        await ctx.popup(researchModal)

    #Confirm Research Modal
    @interactions.extension_modal("modal_research")
    async def modal_research_save(self, ctx:interactions.ComponentContext, weapon:str, shield:str, armor:str):
        self._logger.debug("Modal Confirmed from: %s", ctx.user.username)
        self._logger.debug("Arguments: %s", str((weapon,shield,armor)))

        if not self._auth.check(ctx.user.id, "research"):
            return

        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 

        self._db.setResearch(playerId,weapon,shield,armor)

        #Workaround get playerName from Title
        statsEmbed,statsButtons = self._getStatsContent(ctx.message.embeds[0].title)

        #edit original message
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        #confirm modal
        await ctx.send()

    def _getEmbedValueString(self, data, diff):
        #get largest number
        maxLenghtData = len(max(data, key=len))

        result = "`"

        for elementData,elementDiff in zip(data,diff):
            result += elementData.ljust(maxLenghtData) + " " + elementDiff + "\n"

        return result + "`"

    def _getPlanetFields(self, playerId:str):
        planetData = self._db.getUserPlanets(playerId)

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
            planetEmbeds[0].value += f"{planet[2]}:{planet[3]}:{planet[4]}\n"
            planetEmbeds[1].value += f"-\n" #WIP
            planetEmbeds[2].value += f"-\n" #WIP
        
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

    def _getCurrentPlayerStats(self, playerStats):
        currentRank = [
            self._formatNumber(playerStats[1]),
            self._formatNumber(playerStats[5]),
            self._formatNumber(playerStats[3]),
            self._formatNumber(playerStats[9]),
            self._formatNumber(playerStats[7]),
        ]

        currentScore = [
            self._formatNumber(playerStats[2]),
            self._formatNumber(playerStats[6]),
            self._formatNumber(playerStats[4]),
            self._formatNumber(playerStats[10]),
            self._formatNumber(playerStats[8]),
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

    def _formatNumber(self, number):
        return f"{number:,}".replace(",",".")

def setup(client, args):
    Stats(client, args)