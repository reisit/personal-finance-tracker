from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem
import json
from pathlib import Path
import os
import mysql.connector
from mysql.connector import errorcode


BASE_DIR = Path(__file__).parent 

config_path = BASE_DIR / 'PersonalFinanceTracker' / 'App' / 'functions' / 'config.json'

with config_path.open(encoding='utf-8') as f:
    config = json.load(f)

def clear():
    return os.system('cls') if os.name == 'nt' else os.system('clear')

def start():
    while True:
        op                  =  input("Insert host (default: 'localhost'): ")
        config['host']      =  "localhost" if op in ['', ' '] else op

        op                  =  input("Insert user (default: 'root'): ")
        config['user']      =  "root" if op in ['', ' '] else op

        op                  =  input("Insert password (default: 'admin'): ")
        config['password']  =  "admin" if op in ['', ' '] else op

        op                  =  input("Insert port (default: '3306'): ")
        config['port']      =  "3306" if op in ['', ' '] else op

        clear()

        print(f"Data inserted:\n\thost: '{config['host']}',\n\tuser: '{config['user']}',\n\tpassword: '{config['password']}',\n\tport: '{config['port']}'")

        op = input('continue? (y/n): ')
        
        clear()

        if op in ['y', 'Y']: 
            break

    data = {
         'host': config['host'],
         'user': config['user'],
         'password': config['password'],
         # 'port': config['port']
    }

    try:
         conn   = mysql.connector.connect(**data)
         cursor = conn.cursor()

         cursor.execute(
              f"CREATE DATABASE IF NOT EXISTS `{config['database']}` "
              "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
         )

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid data inserted")
        else:
            print("Error:", err)

    finally:
        cursor.close()
        conn.close()


    with config_path.open("w", encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    
menu = ConsoleMenu("Menu", "Select an option")
menu.append_item(FunctionItem("Start", start))
menu.show()