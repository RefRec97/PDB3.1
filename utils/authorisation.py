import interactions
import logging
from utils.db import DB
import config

class Authorization():
    NOT_MAINTAINED = -1
    OWNER = 1
    ADMIN = 2
    ADMIN_COMMAND_LIST = ("update","shutdown","admin","auth", "Auth","add_update_channel")
    USER = 3
    USER_COMMAND_LIST = ("stats", "planet", "chart", "research", "alliance", "moon", "features", "inactive", "alliance_position", "notify")

    NOT_AUTHORIZED_EMBED = interactions.Embed(
        title="Nicht Authorisiert",
        description= f"Fehler? Bitte mir schreiben -> <@!{config.ownerId}>",
    )

    def __init__(self, db:DB):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")
        self._db:DB = db
        
    
    #Workaround implementation
    #currentyl no check hooks available
    def check(self, userId: int, command: str):
        self._logger.debug("Check userId: %s, with command %s", str(userId), command)

        #Read Database
        role = self._db.getAuthRole(str(userId))

        #owner check
        if role == self.OWNER:
            self._logger.debug("Verified Owner")
            return True
        
        #Admin
        if role == self.ADMIN:
            self._logger.debug("Verified Admin")
            return command in self.ADMIN_COMMAND_LIST or command in self.USER_COMMAND_LIST
    
        #User
        if role == self.USER:
            self._logger.debug("Verified User")
            return command in self.USER_COMMAND_LIST

        #Unknown User
        if role == self.NOT_MAINTAINED:
            self._logger.debug("User not Found")
            return False

        #failsave for unknown Role
        self._logger.debug("Undefined Group")
        return False

    def add(self, userId:int, role:int):
        return self._db.setAuthorization(str(userId), role)

