
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
    

    async def notify(self, type, message, discordId=None):

        for data in self._db.getNotifyByType(type):
            id = data[0]
            guildId = data[2]
            
            if type == Notify.CHANNEL:
                target = await interactions.get(self._client, interactions.Channel, object_id=id)

            elif type == Notify.EXPO_SIZE:
                target = await interactions.get(self._client, interactions.Member, parent_id=guildId, object_id=id)
            
            elif type == Notify.SENSOR_PHALANX:
                target = await interactions.get(self._client, interactions.Member, parent_id=guildId, object_id=discordId)
                await target.send(embeds=message)
                return
            
            await target.send(message)
    
    async def checkSensor(self,moon,newLevel):

        oldRange = (moon[6]*moon[6]) -1
        newRange = (newLevel*newLevel) -1
        lowerNewRange = (moon[3] - newRange)
        upperNewRange = (moon[3] + newRange)
        lowerOldRange = (moon[3] - oldRange)
        upperOldRange = (moon[3] + oldRange)
        
        #cyclic universe adjustments
        if lowerNewRange < 0:
            lowerNewRange += 400
        if upperNewRange > 400:
            upperNewRange -= 400
        if lowerOldRange < 0:
            lowerOldRange += 400
        if upperOldRange > 400:
            upperOldRange -= 400
        
        players = self._db.getNotifyByType(self.SENSOR_PHALANX)
        for player in players:

            playerPlanets = self._db.getPlayerPlanets(player[3])
            found = False
            field = interactions.EmbedField(
                    inline=False,
                    name="Positionen",
                    value=""
                )
            for planet in playerPlanets:
                #check if planet is
                #   - in same galaxy
                #   - system is in range
                #   - old sensor level is not in range

                if moon[2] == planet[2] and\
                    ( lowerNewRange <= planet[3] or planet[3] <= upperNewRange) and\
                    not ( lowerOldRange <= planet[3] or planet[3] <= upperOldRange):

                    found = True
                    field.value += f"[{planet[2]}\:{planet[3]}\:{planet[4]}](https://pr0game.com/uni2/game.php?page=galaxy&galaxy={planet[2]}&system={planet[3]})\n"

            if found:
                embed = interactions.Embed(
                    title=f"Phalanx Warnung!",
                    description= f"Folgende deiner Planeten ist(sind) in Reichweite",
                    fields = [field]
                )
                await self.notify(self.SENSOR_PHALANX, embed, player[0])

