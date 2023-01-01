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
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Username: %s", username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerData = self._db.getPlayerData(username)
        if not playerData:
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
        name="customchart",
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
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Username: %s", username)

        playerData = self._db.getPlayerData(username)
        if not playerData:
            await ctx.send(f"{username} nicht gefunden")
            return
        
        playerStats = self._db.getPlayerStats(playerData[1])

        rawTypes = [type_1,type_2,type_3,type_4,type_5,type_6,type_7,type_8]
        #remove NONE from types
        types = [element for element in rawTypes if element is not None]

        await ctx.send(self._chartCreator.getChartUrl(playerStats,playerData[2],types))
    

def setup(client, args):
    Chart(client, args)