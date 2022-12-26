from datetime import datetime
import threading
import logging

import urllib.request, json 
from utils.player import PlayerStats
from utils.db import DB

class Update():
    def __init__(self, db:DB):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._db:DB = db
        self._running = True
        self._done = False
        
        #kickstart Clock
        self._clock()
        
    def stop(self):
        self._logger.debug("Stopping Clock")
        #stop restarting the Timer
        self._running = False

    def force(self):
        self._updateStats()

    def _clock(self):
        if self._running:
            #Runs every 10 second
            threading.Timer(10, self._clock).start()

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
                    self._updateStats()
        else:
            self._done = False

    
    def _updateStats(self):
        self._logger.info("Starting Update")
        players = []
        with urllib.request.urlopen("https://pr0game.com/stats_Universe_2.json") as url:
            statsData = json.loads(url.read().decode("utf-8"))
            
            for playerData in statsData:
                player = PlayerStats(**playerData)

                #workaround for "null" data
                if not player.allianceName:
                    player.allianceName = '-'
                
                player.playerName = player.playerName

                players.append(player)  

        self._db.setStats(players)
        
        self._logger.info("Update complete")
        


