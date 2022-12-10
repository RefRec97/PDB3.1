import psycopg2
from utils.player import PlayerStats
import config



class DB():
    def __init__(self):
        self._conn = psycopg2.connect(host=config.dbHost, database=config.dbDatabase, user=config.dbUser, password=config.dbPassword)
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
                    VALUES (%s, %s, %s, %s, %s) on conflict ("playerId", "playerName") do nothing; """
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

        return self._readOne(sql,(userID,))[0]

    def getUserData(self, userName:str):
        sql = """ SELECT player."playerName", alliance."allianceName", alliance."allianceId", stats.* FROM pdb3.player
                    INNER JOIN pdb3.stats ON stats."playerId" = player."playerId"
                    INNER JOIN pdb3.alliance ON alliance."allianceId" = player."allianceId"
                    WHERE lower(player."playerName")=lower(%s)
                    ORDER BY stats."timestamp" DESC
                    LIMIT 1;"""

        return self._readOne(sql,(userName,))
    

    def getAllianzData(self, allianzName:str):
        sql = """ SELECT alliance."allianceName", player."playerName", player."playerId", stats."rank", stats."score", max(stats."timestamp") 
                    FROM pdb3.alliance
                    INNER JOIN pdb3.player ON player."allianceId" = alliance."allianceId"
                    INNER JOIN pdb3.stats ON stats."playerId" = player."playerId"
                    WHERE lower(alliance."allianceName")= lower(%s)
                    GROUP BY player."playerName", alliance."allianceName",player."playerId", stats."rank", stats."score"
                    ORDER BY stats."score" DESC"""

        return self._read(sql,(allianzName,))

    def getAllAllianceNames(self):
        sql = """ SELECT alliance."allianceName"
                    FROM pdb3.alliance; """

        return self._read(sql)