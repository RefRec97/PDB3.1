
import logging
import interactions
from utils.db import DB

class Notify():

    def __init__(self, client:interactions.client, db:DB):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client:interactions.client = client
        self._db:DB = db
    

    async def notify(self, message):
        for channelId in self._db.getAllNotifyChannels():
            channel = await interactions.get(self._client, interactions.Channel, object_id=channelId[0])
            await channel.send(message)
