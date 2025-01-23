from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'lusherengineeringpartsdatabase'

TABLES = {}
TABLES['partInfo'] = (
    "CREATE TABLE `partInfo` ("
    "  `ID` int(11) NOT NULL AUTO_INCREMENT,"
    "  `Internal_Pin` int(11) ,"
    "  `Updated` varchar(4) DEFAULT 'NO',"
    "  `Reason`  varchar(22) DEFAULT 'Not yet gotten',"
    "  `Manufacturer` varchar(255),"
    "  `Manufacturer_Part_Number` varchar(255),"
    "  `Supplier` varchar(255),"
    "  `Supplier_Part_Number` varchar(255),"
    "  `Part_Category` varchar(255),"
    "  `Cost_1pc` varchar (8),"
    "  `Cost_100pc` varchar (8),"
    "  `Cost_1000pc` varchar (8),"
    "  `Stock` varchar(11),"
    "  `Tags` varchar(1000) DEFAULT '0',"
    "  PRIMARY KEY (`ID`)"
    ") ENGINE=InnoDB")


cnx = mysql.connector.connect(host = 'localhost', password = 'mommy1971', user = 'root')
cursor = cnx.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)
try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

    
cnx.commit()
cursor.close()
cnx.close()