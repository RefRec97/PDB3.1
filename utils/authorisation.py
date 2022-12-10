from utils.db import DB

class Authorization():
    OWNER = 1
    ADMIN = 2
    ADMIN_COMMAND_LIST = ("update","shutdown","admin","auth","Auth")
    USER = 3
    USER_COMMAND_LIST = ("stats", "alliance")

    def __init__(self, db:DB):
        self._db:DB = db
    
    #Workaround implementation
    #currentyl no check hooks available
    def check(self, userId: int, command: str):

        #Read Database
        role = self._db.getAuthRole(str(userId))

        #owner check
        if role == self.OWNER:
            return True
        
        #Admin
        if role == self.ADMIN:
            return command in self.ADMIN_COMMAND_LIST
    
        #User
        if role == self.USER:
            return command in self.USER_COMMAND_LIST

        #failsave for unknown Role
        return False
    
    def add(self, userId:int, role:int):
        return self._db.addAuthorization(str(userId), role)

