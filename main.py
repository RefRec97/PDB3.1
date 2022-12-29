import interactions
import logging
import datetime
from utils.authorisation import Authorization
from utils.db import DB
from utils.update import Update
from utils.chartCreator import ChartCreator
from utils.statsCreator import StatsCreator
import config



def main():
    #Setup Logger
    logging.basicConfig(
        filename= datetime.datetime.now().strftime("%Y-%m-%d_%H-%M.log"),
        encoding='utf-8',
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    logger.info("Startup")
    #Utils
    db = DB(prod = True)
    update = Update(db)
    authroization = Authorization(db)
    chartCreator = ChartCreator(db)
    statsCreator = StatsCreator(db, chartCreator)
    
    #Create Bot
    client = interactions.Client(token=config.prodToken)

    #Load Commands
    client.load("commands.utils", args=(authroization, update))
    client.load("commands.auth", args=(authroization))
    client.load("commands.stats", args=(authroization, db, statsCreator, chartCreator))
    client.load("commands.planet", args=(authroization, db, statsCreator))
    client.load("commands.chart", args=(authroization, db, chartCreator))


    #Start Bot
    logger.info("Initialization complete, starting client")
    client.start()

if __name__ == "__main__":
    main()