import psycopg2
from utils.player import PlayerStats
import config



class DB():
    def __init__(self, db):
        self._conn = psycopg2.connect(host=config.dbHost, database=db, user=config.dbUser, password=config.dbPassword)
        self._cur = self._conn.cursor()

    def _read(self, sql, data=None):
        self._cur.execute(sql,data)
        return self._cur.fetchall()
    
    def _readOne(self, sql, data):
        self._cur.execute(sql,data)
        return self._cur.fetchone()

    def _write(self, sql, data):
        self._cur.execute(sql,data)
        self._conn.commit()
        
    def writeStats(self, players:list):
        #ToDo: performance
        for player in players:
            self._writePlayer(player)
            self._writeAllianz(player)
            self._writeStats(player)
        
    def _writePlayer(self, player:PlayerStats):
        sql = """INSERT INTO pdb3.player(
                    "playerId", "playerName", "playerUniverse", "playerGalaxy", "allianceId")
                    VALUES (%s, %s, %s, %s, %s) on conflict ("playerId", "playerName", "allianceId") do nothing; """
        self._write(sql,(player.playerId, player.playerName,player.playerUniverse,
                         player.playerGalaxy, player.allianceId))

    def _writeAllianz(self, player:PlayerStats):
        sql = """INSERT INTO pdb3.alliance(
                    "allianceId", "allianceName")
                    VALUES (%s, %s) on conflict ("allianceId", "allianceName") do nothing; """
        
        self._write(sql,(player.allianceId, player.allianceName))

    def _writeStats(self, player:PlayerStats):
        sql = """INSERT INTO pdb3.stats(
                    "rank", "score", "researchRank", "researchScore", "buildingRank", "buildingScore",
                    "defensiveRank", "defensiveScore", "fleetRank", "fleetScore", "battlesWon", "battlesLost",
                    "battlesDraw", "debrisMetal", "debrisCrystal", "unitsDestroyed", "unitsLost", "playerId")
                    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        
        self._write(sql,(player.rank, player.score, player.researchRank, player.researchScore, player.buildingRank,
                         player.buildingScore, player.defensiveRank, player.defensiveScore, player.fleetRank,
                         player.fleetScore, player.battlesWon, player.battlesLost, player.battlesDraw,
                         player.debrisMetal, player.debrisCrystal, player.unitsDestroyed, player.unitsLost,
                         player.playerId))

    def addAuthorization(self, userId:str , role:int):
        sql = """INSERT INTO pdb3.authorization(
                    "userId", "roleId")
                    VALUES (%s, %s) ON CONFLICT ("userId") DO UPDATE
                        SET "roleId" = excluded."roleId";"""
        
        self._write(sql,(userId, role))

    def getAuthRole(self, userID:str):
        sql = """ SELECT "roleId" FROM pdb3.authorization
	                WHERE "userId" = %s;"""

        try:
            return self._readOne(sql,(userID,))[0]
        except:
            return -1

    def getUserData(self, userName:str):
        sql = """ SELECT player."playerName", alliance."allianceName", alliance."allianceId", stats.* FROM pdb3.player
                    INNER JOIN pdb3.stats ON stats."playerId" = player."playerId"
                    INNER JOIN pdb3.alliance ON alliance."allianceId" = player."allianceId"
                    WHERE lower(player."playerName")=lower(%s)
                    ORDER BY stats."timestamp" DESC
                    LIMIT 1;"""

        return self._readOne(sql,(userName,))
    
    def getUserPlanets(self, userId:str):
        sql = """SELECT * FROM pdb3.planet
	        WHERE planet."playerId" = %s"""

        return self._read(sql,(userId,))

    def getuserId(self, userName:str):
        sql = """ SELECT * FROM pdb3.player
            WHERE lower(player."playerName")=lower(%s)
            ORDER BY player."timestamp" DESC
            LIMIT 1;"""

        return self._readOne(sql,(userName,))

    def updatePlanet(self, userId:str, galaxy:int, system:int, position:int):
        sql = """INSERT INTO pdb3.planet(
            "playerId", "galaxy", "system", "position", "moon", "sensorPhalanx")
            VALUES ( %s, %s, %s, %s, %s, %s) 
            on conflict ("galaxy", "system", "position") DO UPDATE 
            SET "playerId" = excluded."playerId" ;"""
        
        self._write(sql,(userId, galaxy, system, position, False , 0 ))

    def delPlanet(self, userId:str, galaxy:int, system:int, position:int):
        sql = """DELETE FROM pdb3.planet
            WHERE planet."playerId" = %s AND
                planet."galaxy" = %s AND
                planet."system" = %s AND
                planet."position" = %s;"""

        self._write(sql,(userId, galaxy, system, position))

