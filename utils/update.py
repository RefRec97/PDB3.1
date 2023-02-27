from datetime import datetime
import asyncio
import logging

import urllib.request, json 
from utils.player import PlayerStats
from utils.db import DB
from utils.notify import Notify
from utils.timer import Timer

class Update():
    def __init__(self, db:DB, notify:Notify):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._db:DB = db
        self._notify:Notify = notify
        self._done = False

        #start Clock
        self._timer = Timer(10, self._tick)
        
        

    
    def stop(self):
        self._logger.debug("Stopping Clock")
        self._timer.cancel()

    async def force(self):
        #update evrything here
        await self._updateStats()
        await self._notify.checkExpoCap()
        

    async def _tick(self):

        hour = datetime.now().hour
        min = datetime.now().minute

        #Run every 6 hours 
        if hour%6 == 0:
            if min == 5 : #add+ (5 minute offset)
                #check if already run this hour
                if not self._done:
                    self._logger.debug("Update timeslot start: %s:%s",hour,min)
                    self._done = True
                    
                    #update evrything here
                    await self._updateStats()
                    await self._notify.checkExpoCap()
        else:
            self._done = False
        
        #restart Timer
        self._timer = Timer(10, self._tick)

    
    async def _updateStats(self):
        self._logger.info("Starting Update")
        try:
            await self._notify.notify(Notify.CHANNEL, "Lade Stats Update")
        except:
            pass
       
        players = []
        with urllib.request.urlopen("https://pr0game.com/stats_Universe_2.json") as url:
            statsData = json.loads(url.read().decode("utf-8"))
            
            for playerData in statsData:
                player = PlayerStats(**playerData)

                #workaround for "null" data
                if not player.allianceName:
                    player.allianceName = '-'
                
                player.playerName = player.playerName
                player.realDebrisMetal = float(player.realDebrisMetal)
                player.realDebrisCrystal = float(player.realDebrisCrystal)

                players.append(player)  

        self._db.setStats(players)
        
        self._logger.info("Update complete")

        try:
            await self._notify.notify(Notify.CHANNEL, "Update geladen")
        except:
            pass
        
        


