
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
                target = await interactions.get(self._client, interactions.Channel, object_id=id)

            elif type == Notify.EXPO_SIZE:
                target = await interactions.get(self._client, interactions.Member, parent_id=guildId, object_id=id)

            await target.send(message)
