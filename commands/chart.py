import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.chartMaker import ChartMaker

class Chart(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
        self._chartMaker:ChartMaker = args[2]
    
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
        chartUrl = self._chartMaker.getChartUrl(playerStats, playerData[2])
        
        await ctx.send(chartUrl)
    

def setup(client, args):
    Chart(client, args)