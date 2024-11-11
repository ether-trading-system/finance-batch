from dotenv import load_dotenv
import os


class EnvLoader:
    def __init__(self) -> None:
        load_dotenv()
        self.DBNAME = os.getenv("DBNAME")
        self.DBUSER = os.getenv("DBUSER")
        self.DBPASS = os.getenv("DBPASS")
        self.DBHOST = os.getenv("DBHOST")
        self.DBPORT = os.getenv("DBPORT")

    def getDBNAME(self) -> str:
        return self.DBNAME

    def getDBUSER(self) -> str:
        return self.DBUSER

    def getDBPASS(self) -> str:
        return self.DBPASS

    def getDBHOST(self) -> str:
        return self.DBHOST

    def getDBPORT(self) -> int:
        return int(self.DBPORT)

    def getDBConnectionProperties(self) -> dict:
        return {
            "dbname": self.DBNAME,
            "user": self.DBUSER,
            "password": self.DBPASS,
            "host": self.DBHOST,
            "port": self.DBPORT,
        }
