import psycopg2
import logging
from utils.player import PlayerStats
import config

class DB():
    def __init__(self, prod:bool):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization in productive Environment: %s",str(prod))

        self._savedAllianceData = []

        self._prod = prod
        self._connect()

    def _connect(self):
        if self._prod:
            try:
                self._conn = psycopg2.connect(host=config.prodDbHost, database=config.prodDatabase, user=config.podDbUser, password=config.prodDbPassword, port=config.pordDbPort)
                self._logger.debug("DB connected")
            except psycopg2.Error as e:
                self._logger.critical("DB connection failed")
                self._logger.critical(e)
        else:
            try:
                self._conn = psycopg2.connect(host=config.devDbHost, database=config.devDatabase, user=config.devDbUser, password=config.devDbPassword, port=config.devDbPort)
                self._logger.debug("DB connected")
            except psycopg2.Error as e:
                self._logger.critical("DB connection failed")
                self._logger.critical(e)
        
        self._cur = self._conn.cursor()

    def _read(self, sql, data=None):
        self._logger.debug("Read from Db")
        self._logger.debug(sql)
        self._logger.debug(data)

        try:
            self._cur.execute(sql,data)
            data = self._cur.fetchall()
        except psycopg2.Error as e:
            self._logger.warning("Failed to Read")
            self._logger.warning(e)

            #Reconect and try again
            self._logger.debug("Retrying read operation")
            try:
                self._connect()
                self._cur.execute(sql,data)
                data = self._cur.fetchall()
            except psycopg2.Error as e:
                self._logger.critical("Retry Read Failed")
                self._logger.critical(e)
        
        self._logger.debug("data read: %s", data)
        return data

    def _readOne(self, sql:str, data:tuple):
        self._logger.debug("Read one from Db")
        self._logger.debug(sql)
        self._logger.debug(data)

        try:
            self._cur.execute(sql,data)
            data = self._cur.fetchone()
        except psycopg2.Error as e:
            self._logger.warning("Failed to read one")
            self._logger.warning(e)
            
            #Reconect and try again
            self._logger.debug("Retrying read operation")
            try:
                self._connect()
                self._cur.execute(sql,data)
                data = self._cur.fetchone()
            except psycopg2.Error as e:
                self._logger.critical("Retry read one Failed")
                self._logger.critical(e)

        self._logger.debug("data read: %s", data)
        return data

    def _write(self, sql:str, data:tuple):
        self._logger.debug("Write into Db")
        self._logger.debug(sql)
        self._logger.debug(data)

        try:
            self._cur.execute(sql,data)
            self._conn.commit()
        except Exception as e:
            
            #Reconect and try again
            self._logger.debug("Retrying write operation")
            try:
                self._connect()
                self._cur.execute(sql,data)
                self._conn.commit()
            except psycopg2.Error as e:
                self._logger.critical("Write Failed")
                self._logger.critical(e)

    def _writePlayer(self, player:PlayerStats):
        sql = """INSERT INTO public.player(
            "playerId", "playerName", "playerUniverse", "playerGalaxy", "allianceId")
            VALUES (%s, %s, %s, %s, %s)
            on conflict ("playerId") DO UPDATE 
            SET "playerName" = excluded."playerName",
                "allianceId" = excluded."allianceId",
                "timestamp" = now();"""
        
        self._write(sql,(player.playerId, player.playerName,player.playerUniverse,
            player.playerGalaxy, player.allianceId))

    def _writeAllianz(self, player:PlayerStats):
        if player.allianceId in self._savedAllianceData:
            return
        self._savedAllianceData.append(player.allianceId)

        sql = """INSERT INTO public.alliance(
            "allianceId", "allianceName")
            VALUES (%s, %s)
            on conflict ("allianceId") DO UPDATE 
            SET "allianceName" = excluded."allianceName",
                "timestamp" = now(); """
        
        self._write(sql,(player.allianceId, player.allianceName))

    def _writeStats(self, player:PlayerStats):
        sql = """INSERT INTO public.stats(
            "rank", "score", "researchRank", "researchScore", "buildingRank", "buildingScore",
            "defensiveRank", "defensiveScore", "fleetRank", "fleetScore", "battlesWon", "battlesLost",
            "battlesDraw", "debrisMetal", "debrisCrystal", "unitsDestroyed", "unitsLost", "playerId")
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        
        self._write(sql,(player.rank, player.score, player.researchRank, player.researchScore, player.buildingRank,
            player.buildingScore, player.defensiveRank, player.defensiveScore, player.fleetRank,
            player.fleetScore, player.battlesWon, player.battlesLost, player.battlesDraw,
            player.debrisMetal, player.debrisCrystal, player.unitsDestroyed, player.unitsLost,
            player.playerId))

    def getAuthRole(self, userID:str):
        sql = """ SELECT "roleId" FROM public.authorization
            WHERE "userId" = %s;"""

        try:
            return self._readOne(sql,(userID,))[0]
        except:
            return -1

    def getPlayerStats(self, playerId:str):
        sql = """SELECT * from public."stats"
            where stats."playerId" = %s
            ORDER BY stats."timestamp" DESC"""

        return self._read(sql,(playerId,))

    def getAlliance(self, allianceName:str):
        sql = """SELECT * from public."alliance"
            where lower(alliance."allianceName") = lower(%s);"""

        return self._readOne(sql,(allianceName,))

    def getAllianceById(self, allianceId:str):
        sql = """SELECT * from public."alliance"
            where alliance."allianceId" = %s;"""

        return self._readOne(sql,(allianceId,))

    def getPlayerPlanets(self, playerId:str):
        sql = """SELECT * FROM public.planet
	        WHERE planet."playerId" = %s"""

        return self._read(sql,(playerId,))

    def getPlayerData(self, userName:str):
        sql = """ SELECT * FROM public.player
            WHERE lower(player."playerName")=lower(%s)"""

        return self._readOne(sql,(userName,))

    def delPlanet(self, playerId:str, galaxy:int, system:int, position:int):
        sql = """DELETE FROM public.planet
            WHERE planet."playerId" = %s AND
                planet."galaxy" = %s AND
                planet."system" = %s AND
                planet."position" = %s;"""

        self._write(sql,(playerId, galaxy, system, position))

    def getResearch(self, playerId:str):
        sql = """SELECT
            WEAPON,
            SHIELD,
            ARMOR,
            COMBUSTION,
            IMPULSE,
            HYPERSPACE,
            "timestamp"
        FROM PUBLIC.RESEARCH
	    WHERE research."playerId" = %s"""

        return self._readOne(sql,(playerId,))

    def getAllianceStats(self, allianceID:str):
        sql = """SELECT DISTINCT ON (player."playerId") stats."timestamp", player."playerId", * from public."stats"
            inner join player on player."playerId" = stats."playerId"
            where player."allianceId" = %s
            ORDER BY player."playerId", stats."timestamp" DESC"""

        return self._read(sql,(allianceID,))

    def getAllAllianceStats(self, allianceID:str):
        sql = """
            SELECT PLAYER."playerName",
                RANK,
                SCORE,
                STATS."researchScore",
                STATS."buildingScore",
                STATS."defensiveScore",
                STATS."fleetScore",
                STATS."timestamp"
            FROM PUBLIC."stats"
            INNER JOIN PLAYER ON PLAYER."playerId" = STATS."playerId"
            WHERE PLAYER."allianceId" = %s
            ORDER BY STATS."timestamp" ASC"""

        return self._read(sql,(allianceID,))

    def getCurrentPlayerData(self):
        sql = """
            SELECT 
                PLAYER."playerName",
                PLAYER."playerId",
                SCORE,
                STATS."timestamp"
            FROM PUBLIC."stats"
            INNER JOIN PLAYER ON PLAYER."playerId" = STATS."playerId"
            WHERE stats."timestamp" > current_date - interval '2' day
            ORDER BY STATS."timestamp" DESC"""
        
        return self._read(sql,())

    def getAlliancePlanets(self, allianceId:str):
        sql = """SELECT 
            PLAYER."playerName",
            PLAYER."playerId",
            PLANET."galaxy",
            PLANET."system",
            PLANET."position",
            PLANET."moon"
        FROM PUBLIC."player"
        INNER JOIN PUBLIC."planet" ON PLANET."playerId" = PLAYER."playerId"
        WHERE PLAYER."allianceId" = %s"""

        return self._read(sql,(allianceId,))
    
    def getNotifyChannel(self, channelId:str):
        sql = """SELECT "channelId"
	        FROM public.notify
            WHERE notify."channelId" = %s"""

        return self._readOne(sql,(channelId,))

    def getAllNotifyChannels(self):
        sql = """SELECT "channelId"
	        FROM public.notify;"""

        return self._read(sql,())

    def setNotifyChannel(self, channelId:str):
        sql = """INSERT INTO public.notify(
            "channelId")
            VALUES (%s);"""

        self._write(sql,(channelId,))

    def setResearchAttack(self, playerId:str, weapon:int, shield:int, armor:int):
        sql = """ INSERT INTO public.research(
            "playerId", "weapon", "shield", "armor")
            VALUES (%s, %s, %s, %s)
            on conflict ("playerId") DO UPDATE 
            SET "weapon" = excluded."weapon",
                "shield" = excluded."shield",
                "armor" = excluded."armor",
                "timestamp" = now();"""
        self._write(sql,(playerId, weapon, shield, armor))
    
    def setResearchDrive(self, playerId:str, combustion:int, impulse:int, hyperspace:int):
        sql = """ INSERT INTO public.research(
            "playerId","combustion", "impulse", "hyperspace")
            VALUES (%s, %s, %s, %s)
            on conflict ("playerId") DO UPDATE 
            SET "combustion" = excluded."combustion",
                "impulse" = excluded."impulse",
                "hyperspace" = excluded."hyperspace",
                "timestamp" = now();"""
        self._write(sql,(playerId, combustion, impulse, hyperspace))

    def setStats(self, players:list):
        self._logger.debug("start Player write")
        
        self._savedAllianceData = []
        #ToDo: performance
        for player in players:
            self._writePlayer(player)
            self._writeAllianz(player)
            self._writeStats(player)
        self._logger.debug("Complete Player write complete count: %s",len(players))
    
    def setAuthorization(self, userId:str , role:int):
        sql = """INSERT INTO public.authorization(
            "userId", "roleId")
            VALUES (%s, %s) ON CONFLICT ("userId") DO UPDATE
                SET "roleId" = excluded."roleId";"""
        
        self._write(sql,(userId, role))
    
    def setPlanet(self, playerId:str, galaxy:int, system:int, position:int):
        sql = """INSERT INTO public.planet(
            "playerId", "galaxy", "system", "position", "moon", "sensorPhalanx")
            VALUES ( %s, %s, %s, %s, %s, %s) 
            on conflict ("galaxy", "system", "position") DO UPDATE 
            SET "playerId" = excluded."playerId" ;"""
        
        self._write(sql,(playerId, galaxy, system, position, False , 0 ))

    def setMoon(self, playerId:str, galaxy:int, system:int, position:int, moon:bool):
        sql = """UPDATE PUBLIC."planet"
            SET MOON = %s
            WHERE PLANET."playerId" = %s
                AND PLANET."galaxy" = %s
                AND PLANET."system" = %s
                AND PLANET."position" = %s;"""
        
        self._write(sql,(moon, playerId, galaxy, system, position, ))
    
    def setSensor(self, playerId:str, galaxy:int, system:int, position:int, sensor:int):
        sql = """UPDATE PUBLIC."planet"
            SET "sensorPhalanx" = %s
            WHERE PLANET."playerId" = %s
                AND PLANET."galaxy" = %s
                AND PLANET."system" = %s
                AND PLANET."position" = %s;"""
        
        self._write(sql,(sensor, playerId, galaxy, system, position, ))