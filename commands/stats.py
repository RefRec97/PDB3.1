import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB

class Stats(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

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
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Username: %s", username)

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
                inline=True,
                name="Type",
                value="Gesamt\nGebäude\nForschung\nFlotte\nVerteidigung\n"
            ),
            interactions.EmbedField(
                inline=True,
                name="Rang",
                value=f"{playerStats[1]}\n{playerStats[5]}\n{playerStats[3]}\n{playerStats[9]}\n{playerStats[7]}\n"
            ),
            interactions.EmbedField(
                inline=True,
                name="Punkte",
                value=f"{playerStats[2]}\n{playerStats[6]}\n{playerStats[4]}\n{playerStats[10]}\n{playerStats[8]}\n"
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

        planetEmbed = interactions.Embed(
            title="Gespeichert",
            description= f"{galaxy}:{system}:{position}",
        )

        await ctx.send(embeds=planetEmbed)

    def _getPlanetEmbeds(self, planetData):
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

        for planet in planetData:
            planetEmbeds[0].value += f"{planet[2]}:{planet[3]}:{planet[4]}\n"
            planetEmbeds[1].value += f"-\n" #WIP
            planetEmbeds[2].value += f"-\n" #WIP
        
        if not planetData:
            planetEmbeds[0].value = "-"
            planetEmbeds[1].value = "-"
            planetEmbeds[2].value = "-"

        return planetEmbeds

    def _formatNumber(self, number):
        return f"{number:,}".replace(",",".")

def setup(client, args):
    Stats(client, args)