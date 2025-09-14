from mysql.connector import pooling
from mysql.connector import Error
import os
import json

base_path = os.path.dirname(__file__)
config_path = os.path.join(base_path, "config.json")

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

class Connection:
    DATABASE = config["database"]
    USERNAME = config["user"]
    PASSWORD = config["password"]
    DB_PORT = config["port"]
    HOST = config["host"]
    POOL_SIZE = 5
    POOL_NAME = 'poolSystem'
    pool = None

    @classmethod
    def createPool(cls):
        if cls.pool is None:
            try:
                cls.pool = pooling.MySQLConnectionPool(
                    pool_name=cls.POOL_NAME,
                    pool_size=cls.POOL_SIZE,
                    host = cls.HOST,
                    port = cls.DB_PORT,
                    database = cls.DATABASE,
                    user = cls.USERNAME,
                    password = cls.PASSWORD
                )
                #print(f'Nombre del pool: {cls.pool.pool_name}')
                #print(f'Tamaño del pool: {cls.pool.pool_size}')
                return cls.pool
            except Error as e:
                print(f'Error in pool: {e}')
        else:
            return cls.pool

    @classmethod
    def getConnection(cls):
        return cls.createPool().get_connection()

    @classmethod
    def closeConnection(cls,con):
        con.close()
        #print ('Connection closed successfully')
    