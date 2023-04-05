import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.chartCreator import ChartCreator
from utils.playerResolve import PlayerResolve

class Chart(interactions.Extension):

    _customChartChoices = [
        interactions.Choice(name="Rank", value=ChartCreator.RANK),
        interactions.Choice(name="Gesamtpunkte", value=ChartCreator.SCORE),
        interactions.Choice(name="Forschungsrang", value=ChartCreator.RESEARCHRANK),
        interactions.Choice(name="Forschungspunkte", value=ChartCreator.RESEARCHSCORE),
        interactions.Choice(name="Gebäuderang", value=ChartCreator.BUILDINGRANK),
        interactions.Choice(name="Gebäudepunkte", value=ChartCreator.BUILDINGSCORE),
        interactions.Choice(name="Verteidigungsrang", value=ChartCreator.DEFENSIVERANK),
        interactions.Choice(name="Verteidigungspunkte", value=ChartCreator.DEFENSIVESCORE),
        interactions.Choice(name="Flottenrang", value=ChartCreator.FLEETRANK),
        interactions.Choice(name="Flottenpunkte", value=ChartCreator.FLEETSCORE),
        interactions.Choice(name="Gewonnene Kämpfe", value=ChartCreator.BATTLESWON),
        interactions.Choice(name="Verlorene Kämpfe", value=ChartCreator.BATTLESLOST),
        interactions.Choice(name="Unentschieden", value=ChartCreator.BATTLESDRAW),
        interactions.Choice(name="Trümmerfeld Metall", value=ChartCreator.DEBRISMETAL),
        interactions.Choice(name="Trümmerfeld Kristall", value=ChartCreator.DEBRISCRYSTAL),
        interactions.Choice(name="Zerstörte Einheiten", value=ChartCreator.UNITSDESTROYED),
        interactions.Choice(name="Verlorene Einheiten", value=ChartCreator.UNITSLOST),
        interactions.Choice(name="Reales Trümmerfeld Metall", value=ChartCreator.REALDEBRISMETAL),
        interactions.Choice(name="Reales Trümmerfeld Kristall", value=ChartCreator.REALDEBRISCRYSTAL),
        interactions.Choice(name="Reale Zerstörte Einheiten", value=ChartCreator.REALUNITSDESTROYED),
        interactions.Choice(name="Reale Verlorene Einheiten", value=ChartCreator.REALUNITSLOST),
    ]

    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
        self._chartCreator:ChartCreator = args[2]
        self._playerResolve: PlayerResolve =args[3]
    
    @interactions.extension_command(
        name="chart",
        description="Chart des Spielers",
        options = [
            interactions.Option(
                name="input",
                description="Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ]
    )
    async def chart(self, ctx: interactions.CommandContext, input:str = None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Username: %s", input)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerId = self._playerResolve.getPlayerId(input)
        if not playerId:
            await ctx.send(f"Spieler nicht gefunden: {input}", ephemeral=True)
            return False
        
        playerData = self._db.getPlayerDataById(playerId)
        playerStats = self._db.getPlayerStats(playerData[1])
        chartUrl = self._chartCreator.getChartUrl(playerStats, playerData[2],
                        [
                            self._chartCreator.RANK,
                            self._chartCreator.SCORE,
                            self._chartCreator.BUILDINGSCORE,
                            self._chartCreator.RESEARCHSCORE,
                            self._chartCreator.FLEETSCORE,
                            self._chartCreator.DEFENSIVESCORE
                        ]
                    )
        
        await ctx.send(chartUrl)
    
    @interactions.extension_command(
        name="c",
        description="Chart des verlinken Spielers",
    )
    @interactions.autodefer(delay=5)
    async def c(self, ctx: interactions.CommandContext):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")

        if not self._auth.check(ctx.user.id, "chart"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerId = self._db.getLinkByDiscordId(str(ctx.user.id))
        if not playerId:
            await ctx.send(f"Verlinkung nicht gefunden. Bitte verlinke zuerst dein Discord mit Pr0game durch /link", ephemeral=True)
            return

        playerData = self._db.getPlayerDataById(playerId[0])
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden", ephemeral=True)
            return False

        playerStats = self._db.getPlayerStats(playerData[1])
        chartUrl = self._chartCreator.getChartUrl(playerStats, playerData[2],
                        [
                            self._chartCreator.RANK,
                            self._chartCreator.SCORE,
                            self._chartCreator.BUILDINGSCORE,
                            self._chartCreator.RESEARCHSCORE,
                            self._chartCreator.FLEETSCORE,
                            self._chartCreator.DEFENSIVESCORE
                        ]
                    )
        await ctx.send(chartUrl)
        
    
    @interactions.extension_command(
        name="custom_chart",
        description="Custom chart des Spielers",
        options =[
            interactions.Option(
                name="input",
                description="Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_1",
                description="Kategorie1",
                required=True,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_2",
                description="Kategorie2",
                required=False,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_3",
                description="Kategorie3",
                required=False,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_4",
                description="Kategorie4",
                required=False,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_5",
                description="Kategorie5",
                required=False,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_6",
                description="Kategorie6",
                required=False,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_7",
                description="Kategorie7",
                required=False,
                choices=_customChartChoices,
            ),
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type_8",
                description="Kategorie8",
                required=False,
                choices=_customChartChoices,
            ),
        ],
    )
    async def customChart(self, ctx: interactions.CommandContext, input:str, type_1:str, type_2:str=None,
                            type_3:str=None, type_4:str=None, type_5:str=None, type_6:str=None, type_7:str=None, type_8:str=None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Username: %s", input)
        
        if not self._auth.check(ctx.user.id, "chart"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerId = self._playerResolve.getPlayerId(input)
        if not playerId:
            await ctx.send(f"Spieler nicht gefunden: {input}", ephemeral=True)
            return
        
        playerData = self._db.getPlayerDataById(playerId)
        playerStats = self._db.getPlayerStats(playerData[1])

        rawTypes = [type_1,type_2,type_3,type_4,type_5,type_6,type_7,type_8]
        #remove NONE from types
        types = [element for element in rawTypes if element is not None]

        await ctx.send(self._chartCreator.getChartUrl(playerStats,playerData[2],types))
    
    @interactions.extension_command(
        name="compare_chart",
        description="Custom chart des Spielers",
        options =[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type",
                description="Kategorie",
                required=True,
                choices=_customChartChoices,
            ),
            interactions.Option(
                name="input1",
                description="1. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="input2",
                description="2. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="input3",
                description="3. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="input4",
                description="4. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="input5",
                description="5. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="input6",
                description="6. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="input7",
                description="7. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="input8",
                description="8. Player ID, Discrod Name oder pr0ganme Username",
                type=interactions.OptionType.STRING,
                required=False
            )
        ],
    )
    async def compareChart(self, ctx: interactions.CommandContext, type:str, input1:str, input2:str,
                           input3:str=None, input4:str=None, input5:str=None, input6:str=None, input7:str=None, input8:str=None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, "chart"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        rawInputs = [input1,input2,input3,input4,input5,input6,input7,input8]
        #remove NONE from names
        names = [element for element in rawInputs if element is not None]

        allPlayerStats = []
        allPlayerNames = []
        for input in names:
            playerId = self._playerResolve.getPlayerId(input)
            if not playerId:
                await ctx.send(f"Spieler nicht gefunden: {input}", ephemeral=True)
                return

            playerData = self._db.getPlayerDataById(playerId)
            allPlayerStats.append(self._db.getPlayerStats(playerData[1]))
            allPlayerNames.append(playerData[2]) #to keep get original upper-/lowercase letters
        

        await ctx.send(self._chartCreator.getCompareChart(allPlayerStats,allPlayerNames,type))

def setup(client, args):
    Chart(client, args)