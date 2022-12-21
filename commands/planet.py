import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB

class Planet(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
    
    
    @interactions.extension_command(
        name="planet",
        description="Speichert ein Planet",
        options = [
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="galaxy",
                description="Galaxy",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.Option(
                name="system",
                description="System",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.Option(
                name="position",
                description="Position",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
        ],
    )
    async def planet(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        #get userId
        userId = self._db.getPlayerData(username)[1]

        #save planet
        self._db.updatePlanet(userId, galaxy, system, position)

        planetEmbed = interactions.Embed(
            title="Gespeichert",
            description= f"{galaxy}:{system}:{position}",
        )

        await ctx.send(embeds=planetEmbed)

    @interactions.extension_command(
        name="delplanet",
        description="Löscht ein Planet",
        options = [
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="galaxy",
                description="Galaxy",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.Option(
                name="system",
                description="System",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.Option(
                name="position",
                description="Position",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
        ],
    )
    async def delPlanet(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))
        
        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        #get userId
        userId = self._db.getPlayerData(username)[1]

        #check if planet exists
        userPlanets = self._db.getUserPlanets(userId)

        #Check and delete if found
        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position):

                # delete planet
                self._db.delPlanet(userId, galaxy, system, position)

                planetEmbed = interactions.Embed(
                    title="Gelöscht",
                    description= f"{galaxy}:{system}:{position}",
                )
                await ctx.send(embeds=planetEmbed)
                return

        #No planet found
        planetEmbed = interactions.Embed(
            title="Kein Planet auf position",
            description= f"{galaxy}:{system}:{position}",
        )
        await ctx.send(embeds=planetEmbed)
        return


def setup(client, args):
    Planet(client, args)