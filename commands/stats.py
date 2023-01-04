import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.statsCreator import StatsCreator
from utils.chartCreator import ChartCreator

class Stats(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
        self._statsCreator:StatsCreator = args[2]
        self._chartCreator:ChartCreator = args[3]
        
    
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
        
        
        statsEmbed,statsComponent = self._statsCreator.getStatsContent(username)
        

        #await ctx.send(f"{username} nicht gefunden")
        
        await ctx.send(embeds=statsEmbed, components=statsComponent)


    #Refresh Button
    @interactions.extension_component("btn_reload")
    async def btn_reload(self, ctx:interactions.ComponentContext):
        self._logger.debug("Button clicked: btn_alliance from %s", ctx.user.username)
        if not self._auth.check(ctx.user.id, "alliance"):
            return
        
        #Workaround get playerName from Title
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(ctx.message.embeds[0].title)

        #edit original message
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        #confirm modal
        await ctx.send()

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
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(ctx.message.embeds[0].title)

        #edit original message
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        #confirm modal
        await ctx.send()

    #Attack research Modal
    @interactions.extension_component("btn_research_attack")
    async def modal_research_attack(self, ctx:interactions.ComponentContext):      
        self._logger.debug("Button clicked: btn_research_attack from %s", ctx.user.username)

        if not self._auth.check(ctx.user.id, "research"):
            return
        
        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 
        currentResearch = self._db.getResearch(playerId)

        if not currentResearch:
            currentResearch = [0,0,0]

        researchModal = interactions.Modal(
            title="Angirffsforschung ändern",
            custom_id="modal_research_attack",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Waffentechnik",
                    custom_id='reasearch_weapon',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[0]
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Schildtechnik",
                    custom_id='reasearch_shield',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[1]
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Raumschiffpanzerung",
                    custom_id='reasearch_armor',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[2]
                )
            ]
        )
        await ctx.popup(researchModal)

    #Confirm Attack Research Modal
    @interactions.extension_modal("modal_research_attack")
    async def modal_research_attack_save(self, ctx:interactions.ComponentContext, weapon:str, shield:str, armor:str):
        self._logger.debug("Modal Confirmed from: %s", ctx.user.username)
        self._logger.debug("Arguments: %s", str((weapon,shield,armor)))

        if not self._auth.check(ctx.user.id, "research"):
            return

        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 

        self._db.setResearchAttack(playerId,weapon,shield,armor)

        #Workaround get playerName from Title
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(ctx.message.embeds[0].title)

        #edit original message
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        #confirm modal
        await ctx.send()

    #Drive research Modal
    @interactions.extension_component("btn_research_drive")
    async def modal_research_drive(self, ctx:interactions.ComponentContext):      
        self._logger.debug("Button clicked: btn_research_drive from %s", ctx.user.username)

        if not self._auth.check(ctx.user.id, "research"):
            return
        
        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 
        currentResearch = self._db.getResearch(playerId)

        if not currentResearch:
            currentResearch = [0,0,0,0,0,0]

        researchModal = interactions.Modal(
            title="Triebwerksforschung ändern",
            custom_id="modal_research_drive",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Verbrennungstriebwerk",
                    custom_id='reasearch_combustion',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[3]
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Impulstriebwerk",
                    custom_id='reasearch_impulse',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[4]
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Hyperraumantrieb",
                    custom_id='reasearch_hyperspace',
                    required=True,
                    min_length=1,
                    placeholder='1',
                    value=currentResearch[5]
                )
            ]
        )
        await ctx.popup(researchModal)
    
    #Confirm Drive Research Modal
    @interactions.extension_modal("modal_research_drive")
    async def modal_research_drive_save(self, ctx:interactions.ComponentContext, combustion:str, impulse:str, hyperspace:str):
        self._logger.debug("Modal Confirmed from: %s", ctx.user.username)
        self._logger.debug("Arguments: %s", str((combustion,impulse,hyperspace)))

        if not self._auth.check(ctx.user.id, "research"):
            return

        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 

        self._db.setResearchDrive(playerId,combustion,impulse,hyperspace)

        #Workaround get playerName from Title
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(ctx.message.embeds[0].title)

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
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(value[0])
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        await ctx.send()

    #Alliance Player Select 2
    @interactions.extension_component("allianceplayerselect2")
    async def alliancePlayerSelect2(self, ctx:interactions.ComponentContext, value):
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(value[0])
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        await ctx.send()

    #Alliance Player Select 3
    @interactions.extension_component("allianceplayerselect3")
    async def alliancePlayerSelect3(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(value[0])
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        await ctx.send()

    #Alliance Player Select 4
    @interactions.extension_component("allianceplayerselect4")
    async def alliancePlayerSelect4(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(value[0])
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        await ctx.send()

    #Alliance Player Select 5
    @interactions.extension_component("allianceplayerselect5")
    async def alliancePlayerSelect5(self, ctx:interactions.ComponentContext, value): 
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(value[0])
        await ctx.message.edit(embeds=statsEmbed, components=statsButtons)
        await ctx.send()

    @interactions.extension_command(
        name="inactive",
        description="Potentiell inaktive Spieler",
        options = [
            interactions.Option(
                name="lowerlimit",
                description="Unteres Punkte Limit",
                type=interactions.OptionType.INTEGER,
                required=False
            ),
        ],
    )
    async def inactive(self, ctx: interactions.CommandContext, lowerlimit:int = 1000):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerData = self._db.getCurrentPlayerData()

        #Group Data by playerId
        groupedData = {}
        for datapoint in playerData:
            if not datapoint[1] in groupedData:
                groupedData[datapoint[1]] = {
                    "playerName": datapoint[0],
                    "userId": datapoint[1],
                    "scores": [],
                }
            groupedData[datapoint[1]]["scores"].append(datapoint[2])

        inactiveEmbed,inactiveComponent = self._getInactiveContent(groupedData, lowerlimit)

        await ctx.send(embeds=inactiveEmbed, components=inactiveComponent)     


    def _getInactiveContent(self, inactiveData:dict, lowerLimit:int):
        inactivePlayers = []
        for playerData in inactiveData.values():
            count = 0
            scores = playerData["scores"]
            for idx,datapoint in enumerate(scores[:-2]):
                if datapoint <= scores[idx+1] and datapoint > lowerLimit:
                    count +=1
                else:
                    #Point increase
                    break
                
                if count >= 4:
                    inactivePlayers.append(playerData)
                    break
        
        inactiveEmbed = interactions.Embed(
            title= f"Inaktive Spieler ",
            description= f"Punkte > {lowerLimit}",
            fields=self._getInactiveEmbedFields(inactivePlayers)
        )
        return (inactiveEmbed,None)

    def _getInactiveEmbedFields(self,inactivePlayers):
        inactiveFields = []
        fieldValue = ""
        for idx,inactivePlayer in enumerate(inactivePlayers):
            if idx%10 == 0 and fieldValue:
                inactiveFields.append(
                    interactions.EmbedField(
                        name="Name",
                        value=fieldValue,
                        inline=True
                    )
                )
                fieldValue = ""
            
            fieldValue+=inactivePlayer["playerName"] + "\n"
        
        #Add not fully filled Field (if exist)
        if fieldValue:
            inactiveFields.append(
                interactions.EmbedField(
                    name="Name",
                    value=fieldValue,
                    inline=True
                )
            )
            
        return inactiveFields

    def _getAllianceContent(self,allianceName:str):
        allianceData = self._db.getAlliance(allianceName)
        if not allianceData:
            return False

        allAllianceData = self._db.getAllAllianceStats(allianceData[1])
        allianceUserData = self._db.getAllianceStats(allianceData[1])
        allianceUserData.sort(key=lambda a: a[3]) #sort by Rank
        
        #Create Embed
        allianceEmbed = interactions.Embed(
            title=f"{allianceData[2]}",
            description= f"Mitglieder: {len(allianceUserData)}",
            fields=self._getTopAlliancePlayerFields(allianceUserData),
            timestamp=allianceUserData[0][0],
            thumbnail=interactions.EmbedImageStruct(
                url=self._chartCreator.getAllianceUrl(allAllianceData,allianceData[2]),
                height=720,
                width=420
            )
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
        top10Fields = [
            interactions.EmbedField(
                inline=True,
                name="Top 10 Spieler",
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
        
        for player in allianceData[:10]:
            top10Fields[0].value += player[24] + "\n"
            top10Fields[1].value += self._statsCreator.formatNumber(player[3]) + "\n"
            top10Fields[2].value += self._statsCreator.formatNumber(player[4]) + "\n"
        
        return top10Fields

def setup(client, args):
    Stats(client, args)