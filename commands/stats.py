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
        
        await ctx.send(embeds=statsEmbed, components=statsComponent)

    def _getStatsContent(self, playerName:str):

        playerData = self._db.getPlayerData(playerName)
        if not playerData:
            return False
        
        playerStats = self._db.getPlayerStats(playerData[1])
        allianceData = self._db.getAllianceData(playerData[5])

        #Embed Fields
        statsFields = [
            interactions.EmbedField(
                inline=False,
                name="Gesamt",
                value=f"`{playerStats[1]:4} - {self._formatNumber(playerStats[2])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Gebäude",
                value=f"`{playerStats[5]:4} - {self._formatNumber(playerStats[6])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Forschung",
                value=f"`{playerStats[3]:4} - {self._formatNumber(playerStats[4])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Flotte",
                value=f"`{playerStats[9]:4} - {self._formatNumber(playerStats[10])}`"
            ),
            interactions.EmbedField(
                inline=False,
                name="Verteidigung",
                value=f"`{playerStats[7]:4} - {self._formatNumber(playerStats[8])}`"
            )
        ]

        #Add Planet Data
        planetData = self._db.getUserPlanets(playerData[1])
        statsFields += self._getPlanetEmbeds(planetData)

        #Create Embed
        statsEmbed = interactions.Embed(
            title=f"{playerData[2]}",
            description= f"{playerData[1]}\n{allianceData[2]}", #PlayerId and Alliance Name
            fields = statsFields,
            timestamp=playerStats[19]
        )

        statsComponent = interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label='Planet Hinzufügen',
            custom_id='btn_planet'
        )
        return (statsEmbed, statsComponent)

    #Planet Modal
    @interactions.extension_component("btn_planet")
    async def modal_planet(self, ctx:interactions.ComponentContext):        
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
                    placeholder='1-200',
                    required=True,
                    min_length=1,
                    max_length=3
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="Galaxy",
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
        if not self._auth.check(ctx.user.id, "planet"):
            return

        #Workaround get PlayerId from Description
        playerId = ctx.message.embeds[0].description.split('\n')[0] 

        self._db.updatePlanet(playerId, galaxy ,system, position)

        planetEmbed = interactions.Embed(
            title="Gespeichert",
            description= f"{galaxy}:{system}:{position}",
        )

        await ctx.send(embeds=planetEmbed)

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