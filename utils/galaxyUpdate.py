import psycopg2
import json
import datetime

import sys
sys.path.append("..")
import config



_conn = psycopg2.connect(host=config.prodDbHost, database=config.prodDatabase, user=config.podDbUser, password=config.prodDbPassword, port=config.pordDbPort)
_cur = _conn.cursor()


    

def updatePlanet(playerId:str, galaxy:int, system:int, position:int, moon:bool, timestamp:datetime):
    sql = """INSERT INTO PUBLIC.PLANET(
        "playerId",
        "galaxy",
        "system",
        "position",
        "moon",
        "timestamp")
    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT ("galaxy", "system", "position") DO
    UPDATE
    SET "playerId" = EXCLUDED."playerId",
        "galaxy" = EXCLUDED."galaxy",
        "system" = EXCLUDED."system",
        "position" = EXCLUDED."position",
        "moon" = EXCLUDED."moon",
        "timestamp" = EXCLUDED."timestamp" """
    
    _write(sql,(playerId, galaxy, system, position, moon, timestamp))


def getAllPlanets():
    sql = """SELECT "playerId",
        "galaxy",
        "system",
        "position",
        "moon",
        "timestamp"
    FROM PUBLIC.PLANET"""
    
    return _read(sql,())


def _write(sql, data):
    _cur.execute(sql,data)
    _conn.commit()


def _read(sql, data):
    _cur.execute(sql,data)
    data = _cur.fetchall()

    return data

def isNotEqualPlanet(p1,p2):
    
    if p1["playerId"] != p2["playerId"]:
        return True
    if p1["moon"] != p2["moon"]:
        return True

    return False

def main():

    changes = 0
    skipped = 0
    newmoon = 0
    moonPos = []

    currentPlanets = {}
    
    for planet in getAllPlanets():
        current = {
            "playerId": str(planet[0]),
            "galaxy": str(planet[1]),
            "system": str(planet[2]),
            "position": str(planet[3]),
            "moon" : planet[4],
            "timestamp":planet[5]
        }

        if current["galaxy"] not in currentPlanets:
            currentPlanets[current["galaxy"]] = {}
        
        if current["system"] not in currentPlanets[current["galaxy"]]:
            currentPlanets[current["galaxy"]][current["system"]] = {}

        if current["position"] not in currentPlanets[current["galaxy"]][current["system"]]:
            currentPlanets[current["galaxy"]][current["system"]][current["position"]] = {}


        currentPlanets[current["galaxy"]][current["system"]][current["position"]] = current


    with open('g4.json',encoding='utf-8') as json_data:
        data = json.load(json_data)

    for key,value in data[0].items():
        gal = key.split(":")[0]
        sys = key.split(":")[1]

        
        print(gal,sys)
        try:
            timestamp = value["timepoint"]/1000
        except:
            print("ERROR ^^")

        for pos,value in value.items():
            #skip timepoint
            if pos == 'timepoint':
                continue

            newTimestamp = datetime.datetime.fromtimestamp(timestamp)

            try:
                if currentPlanets[gal][sys][pos]["timestamp"] >= newTimestamp:
                    #continue on older data in json
                    continue
            except:
                print("no DB entry")


            if value:
                #set
                new = {
                    "playerId": str(value['playerid']),
                    "galaxy": gal,
                    "system": sys,
                    "position": pos,
                    "moon" : value['hasmoon'],
                    "timestamp": newTimestamp
                }
                if isNotEqualPlanet(new,currentPlanets[gal][sys][pos]):
                    updatePlanet(new['playerId'],gal,sys,pos,new["moon"],newTimestamp)
                    changes+=1
                    if new["moon"] == True and currentPlanets[gal][sys][pos]["moon"] == False:
                        newmoon +=1
                        moonPos.append((gal,sys,pos))
                else:
                    skipped +=1
                    
               
            else:
                #del
                new = {
                    "playerId": '-1',
                    "galaxy": gal,
                    "system": sys,
                    "position": pos,
                    "moon" : False,
                    "timestamp": newTimestamp
                }
                if isNotEqualPlanet(new,currentPlanets[gal][sys][pos]):
                    updatePlanet(-1,gal,sys,pos,False,newTimestamp)
                    changes+=1
                else:
                    skipped +=1  

        
    print("changes:")
    print(changes)

    print("skipped:")
    print(skipped)

    print("newMoon:")
    print(newmoon)

    for moon in moonPos:
        print(f'{moon[0]}:{moon[1]}:{moon[2]}')

if __name__ == "__main__":
    main()