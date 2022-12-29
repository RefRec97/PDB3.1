import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.statsCreator import StatsCreator

class Planet(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
        self._statsCreator:StatsCreator = args[2]
    
    
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
        self._db.setPlanet(userId, galaxy, system, position)
        
        statsEmbed,statsButtons = self._statsCreator.getStatsContent(username)
        await ctx.send(embeds=statsEmbed, components=statsButtons)

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
        userPlanets = self._db.getPlayerPlanets(userId)

        #Check and delete if found
        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position):

                # delete planet
                self._db.delPlanet(userId, galaxy, system, position)

                statsEmbed,statsButtons = self._statsCreator.getStatsContent(username)
                await ctx.send(embeds=statsEmbed, components=statsButtons)
                return

        #No planet found
        planetEmbed = interactions.Embed(
            title="Kein Planet auf position",
            description= f"{galaxy}:{system}:{position}",
        )
        await ctx.send(embeds=planetEmbed)
        return

    @interactions.extension_command(
        name="moon",
        description="Speichert ein Mond",
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
    async def moon(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        #get userId
        userId = self._db.getPlayerData(username)[1]

        #check if planet exist
        userPlanets = self._db.getPlayerPlanets(userId)

        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position):

                self._db.setMoon(userId,galaxy,system,position,True)

                statsEmbed,statsButtons = self._statsCreator.getStatsContent(username)
                await ctx.send(embeds=statsEmbed, components=statsButtons)
                return

        #No planet found
        moonEmbed = interactions.Embed(
            title="Kein Planet auf position",
            description= f"{galaxy}:{system}:{position}",
        )
        await ctx.send(embeds=moonEmbed)

    @interactions.extension_command(
        name="delmoon",
        description="Speichert ein Mond",
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
    async def delMoon(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        #get userId
        userId = self._db.getPlayerData(username)[1]

        #check if planet exist
        userPlanets = self._db.getPlayerPlanets(userId)

        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position and
                planet[5]):

                self._db.setMoon(userId,galaxy,system,position,False)

                statsEmbed,statsButtons = self._statsCreator.getStatsContent(username)
                await ctx.send(embeds=statsEmbed, components=statsButtons)
                return

        #No planet/moon found
        moonEmbed = interactions.Embed(
            title="Kein Planet/Mond auf position",
            description= f"{galaxy}:{system}:{position}",
        )
        await ctx.send(embeds=moonEmbed)

    @interactions.extension_command(
        name="sensor",
        description="Setzt das Sensor Phalanx Level auf einem Mond",
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
            interactions.Option(
                name="level",
                description="Sensor Phalanx Level",
                type=interactions.OptionType.INTEGER,
                required=True
            )
        ],
    )
    async def sensor(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int, level:int):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        #get userId
        userId = self._db.getPlayerData(username)[1]

        #check if planet exist
        userPlanets = self._db.getPlayerPlanets(userId)

        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position and
                planet[5]):

                self._db.setSensor(userId,galaxy,system,position,level)

                statsEmbed,statsButtons = self._statsCreator.getStatsContent(username)
                await ctx.send(embeds=statsEmbed, components=statsButtons)
                return

        #No planet/moon found
        moonEmbed = interactions.Embed(
            title="Kein Planet/Mond auf position",
            description= f"{galaxy}:{system}:{position}",
        )
        await ctx.send(embeds=moonEmbed)


def setup(client, args):
    Planet(client, args)