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
        name="del_planet",
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
        
        if not self._auth.check(ctx.user.id, "planet"):
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
        name="del_moon",
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

        if not self._auth.check(ctx.user.id, "moon"):
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

        if not self._auth.check(ctx.user.id, "moon"):
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

    @interactions.extension_command(
        name="alliance_position",
        description="Planetenpositionen der Allianz",
        options = [
            interactions.Option(
                name="alliancename",
                description="Allianz Name",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def alliancePosition(self, ctx: interactions.CommandContext, alliancename:str = None):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        self._logger.debug("Alliance name: %s", alliancename)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        allianceData = self._db.getAlliance(alliancename)
        if not allianceData:
            await ctx.send(f"Allianz {alliancename} nicht gefunden")
            return
        
        alliancePlanets = self._db.getAlliancePlanets(allianceData[1])
        
        alliancePlanets
        planetEmbed = interactions.Embed(
            title= "Planeten Positionen",
            description= allianceData[2],
            fields= self._getAlliancePlanetFields(alliancePlanets)
        )
        await ctx.send(embeds=planetEmbed)

    def _getAlliancePlanetFields(self,alliancePlanets):
        sortedPlanets = sorted(alliancePlanets, key = lambda x: (x[2], x[3], x[4]))

        planetFields = []
        fieldValue = ""
        for idx,planet in enumerate(sortedPlanets):
            
            if idx%10 == 0 and fieldValue:
                planetFields.append(
                    interactions.EmbedField(
                        name="Position",
                        value=fieldValue,
                        inline=True
                    )
                )
                fieldValue = ""
            
            fieldValue += f"{planet[2]}\:{planet[3]}\:{planet[4]}"
            if planet[5]: 
                fieldValue += " :new_moon:"
            fieldValue+="\n"
        
        #Add not fully filled Field (if exist)
        if fieldValue:
            planetFields.append(
                interactions.EmbedField(
                    name="Position",
                    value=fieldValue,
                    inline=True
                )
            )
        
        return planetFields

def setup(client, args):
    Planet(client, args)