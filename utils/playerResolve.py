
import logging
from utils.db import DB

class PlayerResolve():

    def __init__(self, db:DB):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._db:DB = db
    
    def getPlayerId(self, input:str):
        """Resolve a player for a given input in the following order:
            1. If input is 4 characters try check for player Id if valid
            2. Else Try to find with links saved on DB
            3. Else try to find with playerName"""

        #Valid PlayerId (4Digits)
        if input.isdigit() and len(input) == 4:
            playerData = self._db.getPlayerDataById(input)
            if playerData:
                return input
        
        #By Discord name
        playerId = self._db.getLinkByName(input)
        if playerId:
            return playerId

        #By pr0game Name
        playerData = self._db.getPlayerDataByName(input)
        if playerData:
            return playerData[1] # ID on pos 1
        

        

    


    