import interactions
from utils.authorisation import Authorization
from utils.db import DB
from utils.update import Update
import config



def main():
    #Utils
    db = DB(config.prodDatabase)
    update = Update(db)
    authroization = Authorization(db)
    
    #Create Bot
    client = interactions.Client(token=config.prodToken)

    #Load Commands
    client.load("commands.utils", args=(authroization, update))
    client.load("commands.auth", args=(authroization))
    client.load("commands.stats", args=(authroization, db))
    client.load("commands.planet", args=(authroization, db))


    #Start Bot
    client.start()
    


if __name__ == "__main__":
    main()