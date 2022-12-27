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
            interactions.Button(
                style=interactions.ButtonStyle.PRIMARY,
                label='Allianz',
                custom_id='btn_alliance'
            ),
        ]
        return (statsEmbed, statsComponents)

    #Alliance Button
    @interactions.extension_component("btn_alliance")
    async def btn_alliance(self, ctx:interactions.ComponentContext):   
        self._logger.debug("Button clicked: btn_alliance from %s", ctx.user.username)
        if not self._auth.check(ctx.user.id, "alliance"):
            return
        
        #Get Alliance Name from Description
        allianceName = ctx.message.embeds[0].description.split('\n')[1]
        allianceEmbed,allianceComponent = self._getAllianceContent(allianceName)

        #edit original message
        await ctx.message.edit(embeds=allianceEmbed,components=interactions.spread_to_rows(*allianceComponent))
        #confirm modal
        await ctx.send()

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

        self._db.setPlanet(playerId, galaxy ,system, position)

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

    @interactions.extension_command(
        name="alliance",
        description="Stats einer Alliance",
        options = [
            interactions.Option(
                name="alliance",
                description="Allianz Name",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def alliance(self, ctx: interactions.CommandContext, alliance:str = None):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("AllianceName: %s", alliance)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        try:
            allianceEmbed,allianceComponent = self._getAllianceContent(alliance)
        except Exception as e:
            self._logger.warning("Alliance content may have an Error")
            self._logger.warning(e)
            await ctx.send(f"{alliance} nicht gefunden")
            return
        
        await ctx.send(embeds=allianceEmbed, components=interactions.spread_to_rows(*allianceComponent))

    #Alliance Player Select 1
    @interactions.extension_component("allianceplayerselect1")
    async def alliancePlayerSelect1(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._getStatsContent(value[0])
        await ctx.send(embeds=statsEmbed, components=statsButtons)

    #Alliance Player Select 2
    @interactions.extension_component("allianceplayerselect2")
    async def alliancePlayerSelect2(self, ctx:interactions.ComponentContext, value):
        statsEmbed,statsButtons = self._getStatsContent(value[0])
        await ctx.send(embeds=statsEmbed, components=statsButtons)

    #Alliance Player Select 3
    @interactions.extension_component("allianceplayerselect3")
    async def alliancePlayerSelect3(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._getStatsContent(value[0])
        await ctx.send(embeds=statsEmbed, components=statsButtons)

    #Alliance Player Select 4
    @interactions.extension_component("allianceplayerselect4")
    async def alliancePlayerSelect4(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._getStatsContent(value[0])
        await ctx.send(embeds=statsEmbed, components=statsButtons)

    #Alliance Player Select 5
    @interactions.extension_component("allianceplayerselect5")
    async def alliancePlayerSelect5(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._getStatsContent(value[0])
        await ctx.send(embeds=statsEmbed, components=statsButtons)

    def _getAllianceContent(self,allianceName:str):
        allianceData = self._db.getAlliance(allianceName)
        if not allianceData:
            return False

        allianceUserData = self._db.getAllianceStats(allianceData[1])
        allianceUserData.sort(key=lambda a: a[3]) #sort by Rank

        #Create Embed
        allianceEmbed = interactions.Embed(
            title=f"{allianceData[2]}",
            description= f"Mitglieder: {len(allianceUserData)}",
            fields=self._getTopAlliancePlayerFields(allianceUserData),
            timestamp=allianceUserData[0][0]
        )

        playerSelectMenus = self._getAlliancePlayerSelect(allianceUserData)

        return allianceEmbed,playerSelectMenus

    def _getAlliancePlayerSelect(self, allianceDat:tuple):
        playerSelectMenus = []
        selectOptions = []

        # max amount of Rows = 5
        # max amount of Select Options = 25
        # max player for Selection = 5*25
        customIdnumber = 1
        for idx,user in enumerate(allianceDat[:5*25]):
            if idx%25 == 0 and selectOptions:
                playerSelectMenus.append(
                    interactions.SelectMenu(
                        options=selectOptions,
                        placeholder=f"{1+idx-25}-{idx} Spieler",
                        custom_id=f"allianceplayerselect{customIdnumber}",
                    )
                )
                customIdnumber+=1
                selectOptions = []
            

            selectOptions.append(
                interactions.SelectOption(
                    label=user[24],
                    value=user[24],
                )
            )
        
        if len(allianceDat) >5*25:
            start = 4*25 + 1
            end = 5*25
        else:
            start = len(allianceDat)-idx%25
            end = len(allianceDat)

        #append partally filled select menu
        if selectOptions:
            playerSelectMenus.append(
                interactions.SelectMenu(
                    options=selectOptions,
                    placeholder=f"{start}-{end} Spieler",
                    custom_id=f"allianceplayerselect{customIdnumber}",
                )
            )
        return playerSelectMenus

    def _getTopAlliancePlayerFields(self, allianceData:tuple):
        top5Fields = [
            interactions.EmbedField(
                inline=True,
                name="Top 5 Spieler",
                value=""
            ),
            interactions.EmbedField(
                inline=True,
                name="Rang",
                value=""
            ),
            interactions.EmbedField(
                inline=True,
                name="Score",
                value=""
            )
        ]
        
        for player in allianceData[:5]:
            top5Fields[0].value += player[24] + "\n"
            top5Fields[1].value += self._formatNumber(player[3]) + "\n"
            top5Fields[2].value += self._formatNumber(player[4]) + "\n"
        
        return top5Fields

    def _getEmbedValueString(self, data, diff):
        #get largest number
        maxLenghtData = len(max(data, key=len))

        result = "`"

        for elementData,elementDiff in zip(data,diff):
            result += elementData.ljust(maxLenghtData) + " " + elementDiff + "\n"

        return result + "`"

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