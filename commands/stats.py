import interactions
from utils.authorisation import Authorization
from utils.db import DB

class Stats(interactions.Extension):
    def __init__(self, client, args):
        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
    
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
        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        try:
            statsEmbed,statsComponent = self._getStatsContent(username)
        except:
            await ctx.send(f"{username} nicht gefunden")
            return
        
        await ctx.send(embeds=statsEmbed, components= statsComponent)

    def _getStatsContent(self, playerName:str):
        data = self._db.getUserData(playerName)

        if not data:
            return False

        statsFields = [
            interactions.EmbedField(
                inline=False,
                name="Gesamt",
                value=f"`{data[4]:4} - {self._formatNumber(data[5])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Gebäude",
                value=f"`{data[8]:4} - {self._formatNumber(data[9])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Forschung",
                value=f"`{data[6]:4} - {self._formatNumber(data[7])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Flotte",
                value=f"`{data[12]:4} - {self._formatNumber(data[13])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Verteidigung",
                value=f"`{data[10]:4} - {self._formatNumber(data[11])}`"
            )
        ]

        #Add Planet Data
        planetData = self._db.getUserPlanets(data[21]) #21 -> playerId
        statsFields += self._getPlanetEmbeds(planetData)

        #create 
        statsEmbed = interactions.Embed(
            title=f"{data[0]}",
            description= f"{data[1]}",
            fields = statsFields,
            timestamp=data[22]
        )

        return (statsEmbed, None)

    def _getPlanetEmbeds(self, planetData):
        
        planetEmbeds = []
        for planet in planetData:
            planetEmbeds.append( interactions.EmbedField(
                name=f"{planet[2]}:{planet[3]}:{planet[4]}",
                inline=True,
                value='-'
            ))
        
        return planetEmbeds


    def _formatNumber(self, number):
        return f"{number:,}".replace(",",".")
    

def setup(client, args):
    Stats(client, args)