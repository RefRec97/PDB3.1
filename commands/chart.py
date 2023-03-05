import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.chartCreator import ChartCreator

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
    
    @interactions.extension_command(
        name="chart",
        description="Chart des Spielers",
        options = [
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ]
    )
    async def chart(self, ctx: interactions.CommandContext, username:str = None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Username: %s", username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerData = self._db.getPlayerDataByName(username)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
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
        name="c",
        description="Chart des verlinken Spielers",
    )
    @interactions.autodefer(delay=5)
    async def c(self, ctx: interactions.CommandContext):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")

        if not self._auth.check(ctx.user.id, "chart"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerId = self._db.getLink(str(ctx.user.id))
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
                name="username",
                description="Pr0game Username",
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
    async def customChart(self, ctx: interactions.CommandContext, username:str, type_1:str, type_2:str=None,
                            type_3:str=None, type_4:str=None, type_5:str=None, type_6:str=None, type_7:str=None, type_8:str=None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Username: %s", username)
        
        if not self._auth.check(ctx.user.id, "chart"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerData = self._db.getPlayerDataByName(username)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
            return
        
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
                name="username1",
                description="Pr0game Username1",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="username2",
                description="Pr0game Username2",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="username3",
                description="Pr0game Username3",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="username4",
                description="Pr0game Username4",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="username5",
                description="Pr0game Username5",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="username6",
                description="Pr0game Username6",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="username7",
                description="Pr0game Username7",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.Option(
                name="username8",
                description="Pr0game Username8",
                type=interactions.OptionType.STRING,
                required=False
            )
        ],
    )
    async def compareChart(self, ctx: interactions.CommandContext, type:str, username1:str, username2:str,
                           username3:str=None, username4:str=None, username5:str=None, username6:str=None, username7:str=None, username8:str=None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, "chart"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        rawNames = [username1,username2,username3,username4,username5,username6,username7,username8]
        #remove NONE from names
        names = [element for element in rawNames if element is not None]

        allPlayerStats = []
        allPlayerNames = []
        for playerName in names:
            playerData = self._db.getPlayerDataByName(playerName)
            
            if not playerData:
                await ctx.send(f"Spieler nicht gefunden: {playerName}", ephemeral=True)
                return
            allPlayerStats.append(self._db.getPlayerStats(playerData[1]))
            allPlayerNames.append(playerData[2]) #to keep get original upper-/lowercase letters
        

        await ctx.send(self._chartCreator.getCompareChart(allPlayerStats,allPlayerNames,type))
    

def setup(client, args):
    Chart(client, args)