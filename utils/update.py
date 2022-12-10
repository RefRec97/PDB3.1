from datetime import datetime
import threading

import urllib.request, json 
from utils.player import PlayerStats
from utils.db import DB

class Update():
    def __init__(self, db:DB):
        self._db:DB = db
        self._running = True
        self._done = False
        
        #kickstart Clock
        self._clock()
        
    def stop(self):
        #stop restarting the Timer
        self._running = False

    def force(self):
        self._updateStats()

    def _clock(self):
        if self._running:
            #Runs every second
            threading.Timer(1, self._clock).start()

        hour = datetime.now().hour

        #check if 6 hours passed
        if hour%6 == 0:
            #check if already run this hour
            if not self._done:
                self._done = True
                
                #update evrything here
                self._updateStats()
        else:
            self._done = False

    
    def _updateStats(self):
        print("Updating")
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

        self._db.writeStats(players)
        
        print("Update complete")
        


