
import logging
import interactions
from utils.db import DB

class Notify():
    CHANNEL = "1"
    EXPO_SIZE = "2"
    SENSOR_PHALANX = "3"

    def __init__(self, client:interactions.client, db:DB):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client:interactions.client = client
        self._db:DB = db
    

    async def notify(self, type, message):

        for data in self._db.getNotifyByType(type):
            id = data[0]
            guildId = data[2]
            
            if type == Notify.CHANNEL:
                try:
                    target = await interactions.get(self._client, interactions.Channel, object_id=id)
                except:
                    self._logger.error("Failed to get Channel")
                    return

            elif type == Notify.EXPO_SIZE:
                try:
                    target = await interactions.get(self._client, interactions.Member, parent_id=guildId, object_id=id)
                except:
                    self._logger.error("Failed to get User")
                    return
            
            await target.send(message)
    
    async def notifySingleUser(self, message, target):
        
        target = await interactions.get(self._client, interactions.Member, parent_id=target[2], object_id=target[0])
        
        await target.send(embeds=message)

    async def checkSensor(self,moon,newLevel):
        targets = self._db.getNotifyByType(Notify.SENSOR_PHALANX)
        for target in targets:

            playerPlanets = self._db.getPlayerPlanets(target[3])
            found = False
            field = interactions.EmbedField(
                    inline=False,
                    name="Deine Planeten",
                    value=""
                )
            for planet in playerPlanets:
                #check if planet is
                #   - in same galaxy
                #   - system is in range
                #   - old sensor level is not in range

                if moon[2] == planet[2] and\
                    self._isPlanetInSensorRange(moon[3],newLevel,planet[3]) and\
                    not self._isPlanetInSensorRange(moon[3],moon[6],planet[3]):

                    found = True
                    field.value += f"[{planet[2]}\:{planet[3]}\:{planet[4]}](https://pr0game.com/uni2/game.php?page=galaxy&galaxy={planet[2]}&system={planet[3]})\n"

            if found:
                embed = interactions.Embed(
                    title=f"Phalanx Warnung!",
                    description= f"Sensor Phalanx wurde aktualisiert auf Mond: [{moon[2]}\:{moon[3]}\:{moon[4]}](https://pr0game.com/uni2/game.php?page=galaxy&galaxy={moon[2]}&system={moon[3]})",
                    fields = [field]
                )
                await self.notifySingleUser(embed, target)

    async def checkExpoCap(self):
        self._logger.info("Checking expo cap")
        scoreCap = [
            100000,
            1000000,
            5000000,
            25000000,
            50000000,
            75000000,
            100000000
        ]


        lastTopScores = self._db.getScoreForExpo()
        current = lastTopScores[0][0]
        last = lastTopScores[1][0]
        
        for score in scoreCap:
            if last < score and current >= score:
                await self.notify(Notify.EXPO_SIZE, "Info: Expo cap ist erhöht")
    
    def _isPlanetInSensorRange(self, moonSystem, moonLevel, planetSystem):
        if moonLevel == 0:
            return False

        range = (moonLevel*moonLevel) -1
        startSystem = (moonSystem - range)
        endSystem = (moonSystem + range)

        if endSystem > 400 and planetSystem < endSystem-400:
            return 0 < planetSystem < endSystem-400
        
        if startSystem < 0 and planetSystem > startSystem+400:
            return startSystem+400 < planetSystem < 400
            
        return (startSystem <= planetSystem <= endSystem)