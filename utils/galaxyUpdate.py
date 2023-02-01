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


def getPlanet(gal,sys,pos):
    sql = """SELECT
        "playerId",
        "galaxy",
        "system",
        "position",
        "timestamp"
    FROM PUBLIC.PLANET
        WHERE planet."galaxy"= %s
        AND planet."system"= %s
        and planet."position"= %s"""
    
    return _read(sql,(gal,sys,pos))


def _write(sql, data):
    _cur.execute(sql,data)
    _conn.commit()


def _read(sql, data):
    _cur.execute(sql,data)
    data = _cur.fetchone()

    return data


def main():
    with open('data.json',encoding='utf-8') as json_data:
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
            current = getPlanet(gal,sys,pos)
            new = datetime.datetime.fromtimestamp(timestamp)

            try:
                if current[4] >= new:
                    #continue on older data in json
                    continue
            except:
                print("no DB entry")


            if value:
                #set
                updatePlanet(value['playerid'],gal,sys,pos,value['hasmoon'],new)
            else:
                #del
                updatePlanet(-1,gal,sys,pos,False,new)


if __name__ == "__main__":
    main()