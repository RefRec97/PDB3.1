import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.statsCreator import StatsCreator
from utils.notify import Notify

class Planet(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
        self._statsCreator:StatsCreator = args[2]
        self._notify:Notify = args[3]
    
    @interactions.autodefer(delay=5)
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
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        try:
            self._checkValidPosition(galaxy,system,position)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return

        playerData = self._db.getPlayerData(username)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
            return

        #save planet
        self._db.updatePlanet(galaxy,system,position,playerData[1])
        
        await ctx.send("Working...")
        try:
            statsEmbed,statsComponent = self._statsCreator.getStatsContent(username)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return
        
        await ctx.edit("",embeds=statsEmbed, components=statsComponent)

    @interactions.autodefer(delay=5)
    @interactions.extension_command(
        name="del_planet",
        description="Löscht ein Planet",
        options = [
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
    async def delPlanet(self, ctx: interactions.CommandContext, galaxy:int, system:int, position: int):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))
        
        if not self._auth.check(ctx.user.id, "planet"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        try:
            self._checkValidPosition(galaxy,system,position)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return

        self._db.updatePlanet(galaxy,system,position)
        await ctx.send(f"Planet Gelöscht {galaxy}\:{system}\:{position}")

    @interactions.autodefer(delay=5)
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
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        try:
            self._checkValidPosition(galaxy,system,position)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return

        #get userId
        playerData = self._db.getPlayerData(username)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
            return

        #check if planet exist
        userPlanets = self._db.getPlayerPlanets(playerData[1])

        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position):

                self._db.setMoon(playerData[1],galaxy,system,position,True)

                await ctx.send("Working...")
                try:
                    statsEmbed,statsComponent = self._statsCreator.getStatsContent(username)
                except ValueError as err:
                    self._logger.debug(err)
                    await ctx.send(str(err), ephemeral=True)
                    return
                await ctx.edit("",embeds=statsEmbed, components=statsComponent)
                return

        #No planet found
        await ctx.edit(f"Planet für Spieler nicht gefunden: {username}", ephemeral=True)

    @interactions.autodefer(delay=5)
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
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, "moon"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        try:
            self._checkValidPosition(galaxy,system,position)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return

        playerData = self._db.getPlayerData(username)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
            return

        #check if planet exist
        userPlanets = self._db.getPlayerPlanets(playerData[1])

        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position and
                planet[5]):

                self._db.setMoon(playerData[1],galaxy,system,position,False)
                await ctx.send("Working...")
                try:
                    statsEmbed,statsComponent = self._statsCreator.getStatsContent(username)
                except ValueError as err:
                    self._logger.debug(err)
                    await ctx.send(str(err), ephemeral=True)
                    return
                await ctx.edit("",embeds=statsEmbed, components=statsComponent)
                return

        #No planet found
        await ctx.edit(f"Planet für Spieler nicht gefunden: {username}", ephemeral=True)

    @interactions.autodefer(delay=5)
    @interactions.extension_command(
        name="phalanx",
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
    async def phalanx(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int, level:int):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Arguments: %s", str((galaxy,system,position)))

        if not self._auth.check(ctx.user.id, "moon"):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        try:
            self._checkValidPosition(galaxy,system,position)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return

        playerData = self._db.getPlayerData(username)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
            return

        #check if planet exist
        userPlanets = self._db.getPlayerPlanets(playerData[1])

        for planet in userPlanets:
            if (planet[2] == galaxy and 
                planet[3] == system and 
                planet[4] == position and
                planet[5]):
                
                await self._notify.checkSensor(planet,level)
                self._db.setSensor(playerData[1],galaxy,system,position,level)
                
                await ctx.send("Working...")
                try:
                    statsEmbed,statsComponent = self._statsCreator.getStatsContent(username)
                except ValueError as err:
                    self._logger.debug(err)
                    await ctx.send(str(err), ephemeral=True)
                    return
                await ctx.edit("",embeds=statsEmbed, components=statsComponent)
                return

        #No planet/moon found
        await ctx.edit(f"Planet für Spieler nicht gefunden: {username}", ephemeral=True)

    @interactions.extension_command(
        name="in_range",
        description="Zeigt an ob eine Position in reichweite eines Sensor Phalanx ist",
        options = [
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
            )
        ],
    )
    async def inRange(self, ctx: interactions.CommandContext, galaxy:int, system:int):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        try:
            self._checkValidPosition(galaxy,system,1)
        except ValueError as err:
            self._logger.debug(err)
            await ctx.send(str(err), ephemeral=True)
            return

        galaxyMoons = self._db.getAllGalaxyMoons(galaxy)
        if not galaxyMoons:
            await ctx.send(f"Keine Moonde in der Galaxy: {galaxy}", ephemeral=True)
            return

        result = ""
        for moon in galaxyMoons:
            if moon[2] == 0:
                continue
            if self._statsCreator.isPlanetInSensorRange(moon[1],moon[2], system):
                result += f"[{galaxy}\:{moon[1]}](https://pr0game.com/uni2/game.php?page=galaxy&galaxy={galaxy}&system={moon[1]})\n"

        resultEmbed = interactions.Embed(
            title= "Monde In Scanreichweite",
            description= f"für Planet auf Position [{galaxy}\:{system}](https://pr0game.com/uni2/game.php?page=galaxy&galaxy={galaxy}&system={system})",
            fields= [
                        interactions.EmbedField(
                        inline=True,
                        name="Monde:",
                        value=result
                    )
                ]
            )
        
        if not result:
            await ctx.send(f"Keine Monde in Reichweite")
            return
        
        await ctx.send(embeds=resultEmbed)

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
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Alliance name: %s", alliancename)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        allianceData = self._db.getAlliance(alliancename)
        if not allianceData:
            await ctx.send(f"Allianz {alliancename} nicht gefunden")
            return
        
        alliancePlanets = self._db.getAlliancePlanets(allianceData[1])
        
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

    def _checkValidPosition(self, galaxy:int, system:int, position:int):
        
        if galaxy < 1 or galaxy > 4:
            raise ValueError("Galaxy muss zwischen 1 und 4 liegen")
        
        elif system < 1 or system > 400:
            raise ValueError("System muss zwischen 1 und 400 liegen")
        
        elif position < 1 or position > 15:
            raise ValueError("Position muss zwischen 1 und 15 liegen")

        return

def setup(client, args):
    Planet(client, args)