from __future__ import print_function       #Imports necessary to use
import requests
import json
import time
import sys
from urllib.parse import quote
import sshtunnel
import pymysql
import os
from datetime import date

from flask import Flask, request
import threading

mouserKey = os.environ.get('mouserKey')
url = f'https://api.mouser.com/api/v1/search/partnumber?apiKey={mouserKey}'
tempCode = 'ejJLOJrV'

app = Flask(__name__)
# SSH tunnel configuration
SSH_HOST = os.environ.get('SSH_HOST')
SSH_PORT = int(os.environ.get('SSH_PORT'))
SSH_USERNAME = os.environ.get('SSH_USERNAME')
SSH_PASSWORD = os.environ.get('SSH_PASSWORD')

# MySQL database configuration
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
MYSQL_USERNAME = os.environ.get('SSH_USERNAME')
MYSQL_PASSWORD = os.environ.get('SSH_PASSWORD')
MYSQL_DATABASE = "lusher engineering parts database"

@app.route('/')    #Base route so that Vercel doesn't constantly ping either a suppiler or the database
def base():
    return("Default")    #Simply return, Displays Default on Vercel

@app.route('/refreshToken')    
def use_refresh_token():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}    #Creates a list to hold variables. Corresponds to the DigikeyValues Table in the database
            #cnx = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")      #EC@ Database. NOT IN USE
            query = "Select * FROM DigikeyValues"    #Pulls all data from the DigikeyValues table and adds it into different variables.
            cursor = connection.cursor()
            cursor.execute(query)
            for x in cursor:    
                tokenSQL = x      
            token['client_id'] = tokenSQL[0]
            token['client_secret'] = tokenSQL[1]
            token['access_token'] = tokenSQL[2]
            token['refresh_token'] = tokenSQL[3]
            token['expires_in'] = tokenSQL[4]
            token['refresh_token_expires_in'] = tokenSQL[5]
            token['token_type'] = tokenSQL[6]
            url = 'https://api.digikey.com/v1/oauth2/token'     #Given digikey URL to draw out access token
            #print(token['refresh_token'])
            url_data = {                                        #Puts the correct values into the response header
                'refresh_token': token['refresh_token'],
                'client_id': token['client_id'],
                'client_secret': token['client_secret'],
                'redirect_uri': 'https://localhost',
                'grant_type': 'refresh_token'
            }
            response = requests.post(url, data=url_data)    #Makes a request to the API to draw out the information
        # print(response.json())
            if response.status_code == 200:                 #If successful
                print('Successfully gotten Access token')
                response_data = response.json()             
                token['access_token'] = response_data['access_token']       #From the API call push the needed data into the file to store it 
                token['refresh_token'] = response_data['refresh_token']
                token['expires_in'] = response_data['expires_in']
                token['refresh_token_expires_in'] = response_data['refresh_token_expires_in']
                token['token_type'] = response_data['token_type']
                queryRefresh = ("UPDATE DigikeyValues SET access_token = %s, refresh_token = %s, expires_in = %s, refresh_token_expires_in = %s, token_type = %s WHERE client_id = %s")
                refreshDataInfo = (token['access_token'],token['refresh_token'],token['expires_in'],token['refresh_token_expires_in'],token['token_type'],token['client_id'])
                cursor.execute(queryRefresh, refreshDataInfo)    #Updates the DigikeyValues Table so that it can be used next time.
                connection.commit()
                return "Successfully gotten Access token"
            else:       #If failed
                print("Go to https://api.digikey.com/v1/oauth2/authorize?response_type=code&client_id=7nuAFcFkxQANPZevGdx00G4i0rw9gfTg&redirect_uri=https://localhost and gather the Auth code")
                #Must first get the authorization code from the given url. 
                #tempCode = str(input("Enter the auth code"))
                get_access_token(tempCode)   
                return("Refresh Token called, Head to code to enter Auth Code")
        finally:
            # Close the connection
            connection.close()
    

def get_access_token(auth_code):
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
            #cnx = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")      #Currently connect to local database
            query = "Select * FROM DigikeyValues"
            cursor = connection.cursor()
            cursor.execute(query)
            for x in cursor:    
                tokenSQL = x     
            token['client_id'] = tokenSQL[0]
            token['client_secret'] = tokenSQL[1]
            token['access_token'] = tokenSQL[2]
            token['refresh_token'] = tokenSQL[3]
            token['expires_in'] = tokenSQL[4]
            token['refresh_token_expires_in'] = tokenSQL[5]
            token['token_type'] = tokenSQL[6]

            url = 'https://api.digikey.com/v1/oauth2/token'
            url_data = {
                'code': auth_code,
                'client_id': token['client_id'],
                'client_secret': token['client_secret'],
                'redirect_uri': 'https://localhost',
                'grant_type': 'authorization_code'
            }
            #print(url_data)
            response = requests.post(url, data=url_data)
            #print(response.json())
            #print(response.status_code)
            if response.status_code == 200:
                print('Successfully gotten Access token')
                response_data = response.json()
                token['access_token'] = response_data['access_token']
                token['refresh_token'] = response_data['refresh_token']
                token['expires_in'] = response_data['expires_in']
                token['refresh_token_expires_in'] = response_data['refresh_token_expires_in']
                token['token_type'] = response_data['token_type']
                queryRefresh = ("UPDATE DigikeyValues SET access_token = %s, refresh_token = %s, expires_in = %s, refresh_token_expires_in = %s, token_type = %s WHERE client_id = %s")
                refreshDataInfo = (token['access_token'],token['refresh_token'],token['expires_in'],token['refresh_token_expires_in'],token['token_type'],token['client_id'])
                cursor.execute(queryRefresh, refreshDataInfo)
                connection.commit()
            return(response.json())
        finally:
            # Close the connection
            connection.close()
    
    
#use_refresh_token()
#get_access_token(tempCode, token_filename)

failed = 0          #Intitiates variables for later use
gotten = 0
alrExist = 0
misMatch = 0
clean = ""
filter = ""
limitby = ""
misMatching = False
#if conn.is_connected():                            #Used to check if the database connection actually worked
#    print('worked')"

#conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
#cursor = conn.cursor()
"""
#cursor.execute("DESCRIBE electronics_parts")   #Used to find the typing of the original database

#query = "INSERT INTO partinfo (Internal_Pin, Manufacturer, Manufacturer_Part_Number, Supplier, Supplier_Part_Number, Part_Category, Cost_1pc, Cost_100pc, Cost_1000pc, Stock) SELECT InternalPN, Manufacturer, ManufacturerPartNumber, Supplier, SupplierPartNumber1, PartCategory, Cost1pc, Cost100pc, Cost1000pc, PrimaryVendorStock FROM electronics_parts"
#cursor.execute(query)
# Above used to copy info from og table into temp table

query = "SELECT Supplier_Part_Number FROM partInfo"
cursor.execute(query)
id = 0             #Loads the current part numbers into a list
for x in cursor:
    id = id+1       #Counts the number of partnumbers within the table
datanumbers = ['null'] * id     #Intitalzies a list based on that number
id = 0
cursor.execute(query)
for x in cursor:    
    datanumbers[id] = x     #Puts the partnumber into the list
    id = id+1
#print(datanumbers[1])                                     #Used to check if it is correctly printing
"""
@app.route('/Filter', methods = ['POST'])
def Filtering():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            filter = request.form['filter']     #What category are you filtering by. Ex. Manufacturer
            #print(filter)
            limitby = request.form['limitby']   #What value do you want to see. Ex. Texas Instruments+
            type = request.form.get('type', 'ASC')    #ASC or DESC
            filterQuery = "SELECT * FROM electronics_parts WHERE `"+filter+"` = '"+limitby+"' ORDER BY ID "+type
            #print(filterQueryt)
            cursor.execute(filterQuery)
            id = 0             #Loads the filtered data into a list
            for x in cursor:
                id = id+1
            filterData = ['null'] * id
            #print(id)
            id = 0
            cursor.execute(filterQuery)
            for x in cursor:
                filterData[id] = x
                id = id+1
            for i in filterData:
                print(i)        #Prints filtered data
            return(json.dumps(filterData))
        finally:
            # Close the connection
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")

@app.route('/Sort', methods = ['POST'])
def Sorting():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
            cursor = connection.cursor()
            sort = request.form['sort']     #What category do you want sorted. Ex. Manufacturer
            type = request.form.get('type', 'ASC')    #ASC or DESC
            #print(sort)
            sortQuery = "SELECT * FROM electronics_parts ORDER BY `"+sort+"` "+ type + ", ID"
            #print(sortQuery)
            cursor.execute(sortQuery)

            id = 0             #Loads the sorted information into a list
            for x in cursor:
                id = id+1
            sortData = ['null'] * id
            print(id)
            id = 0
            cursor.execute(sortQuery)
            for x in cursor:
                sortData[id] = x
                id = id+1
            for i in sortData:
                print(i)
            return(json.dumps(sortData))
        finally:
            # Close the connection
            connection.close()
    




@app.route('/Tag', methods = ['POST'])
def Tagging():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            prevTag = 0
            updateTag = "UPDATE electronics_parts SET Tags = %s WHERE `Supplier Part Number 1` = %s" 
            upVals = ("1","2")      #1 is the tag while 2 is the partnumber
            tagPart = request.form['partnumber']        #Partnumber where you want to add a tag
            tagValue = request.form['tag']              #What the tag should be
            if(checkDup(tagPart) == False):
                return "Part not found, ensure you are using the Supplier partnumber found within the database."
            tagQuery = "SELECT Tags FROM electronics_parts WHERE `Supplier Part Number 1` = '"+tagPart+"'"
            cursor.execute(tagQuery)
            for x in cursor:
                prevTag = x
            prevTag = str(prevTag).replace("('","")                    #Makes the previous tag a normal string with no extra characters
            prevTag = prevTag.replace("',)","")
            #print(prevTag) 
            if prevTag == "(None,)":
                upVals = (tagValue, tagPart)
            elif prevTag == "":
                upVals = (tagValue,tagPart)
            else:
                if tagValue.count("--")==1:
                    if tagValue.index("--")==0:
                        tagValue = tagValue.replace("--","")
                        tagHold = ", "+tagValue
                        tagHold2 = tagValue
                        tagValue = tagValue + ", "
                        if prevTag.count(tagValue) != 0:
                            prevTag = prevTag.replace(tagValue,"")
                            print(prevTag)
                            upVals = (prevTag, tagPart)
                            cursor.execute(updateTag, upVals)
                            connection.commit()
                            return("Tag Deleted")
                        if prevTag.count(tagHold) != 0:
                            prevTag = prevTag.replace(tagHold,"")
                            print(prevTag)
                            upVals = (prevTag, tagPart)
                            cursor.execute(updateTag, upVals)
                            connection.commit()
                            return("Tag Deleted")
                        if prevTag.count(tagHold2) != 0:
                            prevTag = prevTag.replace(tagHold2,"")
                            print(prevTag)
                            upVals = (prevTag, tagPart)
                            cursor.execute(updateTag, upVals)
                            connection.commit()
                            return("Tag Deleted")
                        return "No such Tag to Delete"
                upVals = (prevTag+", "+tagValue, tagPart)
            cursor.execute(updateTag, upVals)
            connection.commit()
            return("Tag Added")
        finally:
            # Close the connection
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")

@app.route('/Delete', methods=['POST'])
def Deleting():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            delCat = request.form['category']   #Category, you will have to default it to supplier_partnumber
            delVal = request.form['delete']     #Partnumber of what you want to delete
            delQuery = "DELETE FROM electronics_parts WHERE `" + delCat + "` = '"+delVal+"'"
            checkQuery = "SELECT * FROM electronics_parts WHERE `"+ delCat + "` = '"+delVal+"'"
            cursor.execute(checkQuery)
            for x in cursor:
                cursor.execute(delQuery)
                connection.commit()
                return("Part deleted")
            return("No parts found")
        finally:
            # Close the connection
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    

add_info = ("INSERT INTO electronics_parts "
            "(Updated, Reason, Manufacturer, `Manufacturer Part Number`, `Supplier 1`, `Supplier Part Number 1`, `Part Category`, `Cost 1pc`, `Cost 100pc`, `Cost 1000pc`, `Primary Vendor Stock`, `Part Description`, `RoHS Compliant`)"
            "VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s,%s)")
update_info = ("UPDATE electronics_parts SET Updated = %s, Reason = %s, Manufacturer = %s, `Manufacturer Part Number` = %s, `Supplier 1` = %s, `Part Category` = %s, `Cost 1pc` = %s, `Cost 100pc` = %s, `Cost 1000pc` = %s, `Primary Vendor Stock` = %s, `Part Description` = %s, `RoHS Compliant` = %s WHERE `Supplier Part Number 1` = %s")
update_failed = ("UPDATE electronics_parts SET Updated = %s, Reason = %s WHERE `Supplier Part Number 1` = %s")
                 
def checkDup(partnumber):
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            query = "SELECT `Supplier Part Number 1` FROM electronics_parts"
            cursor.execute(query)
            id = 0             #Loads the current part numbers into a list
            for x in cursor:
                id = id+1       #Counts the number of partnumbers within the table
            datanumbers = ['null'] * id     #Intitalzies a list based on that number
            id = 0
            cursor.execute(query)
            for x in cursor:    
                datanumbers[id] = x     #Puts the partnumber into the list
                id = id+1

            #print(partnumber + " Is the partnumber") 
            for x in range(len(datanumbers)):
                clean = str(datanumbers[x]).replace("('","")                    #Cleans up the part numbers to make them just strings with no extra characters
                clean = clean.replace("',)","")
                #print(clean)
                if(partnumber == clean):
                    return True                 #"Part Already Exists in database"
            return False
        finally:
            # Close the connection
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    
    

def get_product_details(partnumber):
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            global misMatch
            #partnumber = quote(partnumber) #it replaces invalid characters in the partnumber
            url = f'https://api.digikey.com/Search/v3/Products/{partnumber}'
            token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
            query = "Select * FROM DigikeyValues"
            cursor.execute(query)
            for x in cursor:    
                tokenSQL = x     
            token['client_id'] = tokenSQL[0]
            token['client_secret'] = tokenSQL[1]
            token['access_token'] = tokenSQL[2]
            token['refresh_token'] = tokenSQL[3]
            token['expires_in'] = tokenSQL[4]
            token['refresh_token_expires_in'] = tokenSQL[5]
            token['token_type'] = tokenSQL[6]
            #print(url)
            
            url_header = {
                'x-digikey-locale': 'en',   
                'X-DIGIKEY-Locale-Site': 'US',
                'X-DIGIKEY-Locale-Currency': 'USD',
                'Authorization': f"{token['token_type']} {token['access_token']}",
                'X-DIGIKEY-Client-Id': token['client_id']
            }

            #print(f'URL {url}\nHeaders: {url_header}\n')
            response = requests.get(url, headers=url_header)
            #print(response.json()['DigiKeyPartNumber'])
            if(response.status_code == 401):
                use_refresh_token()
                time.sleep(1.2)
                token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
                query = "Select * FROM DigikeyValues"
                cursor.execute(query)
                for x in cursor:    
                    tokenSQL = x     
                token['client_id'] = tokenSQL[0]
                token['client_secret'] = tokenSQL[1]
                token['access_token'] = tokenSQL[2]
                token['refresh_token'] = tokenSQL[3]
                token['expires_in'] = tokenSQL[4]
                token['refresh_token_expires_in'] = tokenSQL[5]
                token['token_type'] = tokenSQL[6]
                url_header = {
                'x-digikey-locale': 'en',   
                'X-DIGIKEY-Locale-Site': 'US',
                'X-DIGIKEY-Locale-Currency': 'USD',
                'Authorization': f"{token['token_type']} {token['access_token']}",
                'X-DIGIKEY-Client-Id': token['client_id']
            }
                response = requests.get(url, headers=url_header)
            if (response.status_code == 200):      
                response_dict = response.json()
                print(response.json()['DigiKeyPartNumber'])
                print()
                if(partnumber != response.json()['DigiKeyPartNumber']):
                    misMatch = misMatch + 1
                    print("Mismatch Occured for "+partnumber +"/"+response.json()['DigiKeyPartNumber'] + " :Digi-Key Add")
                    return False
                print(f'Got information for {partnumber}')
                global gotten
                gotten = gotten + 1
                #print("Manufacturer: " + str(response.json()['Manufacturer']['Value']))
                #print("Available: " + str(response.json()['QuantityAvailable']))
                #print("Category: " + str(response.json()['Category']['Value']))
                #print("DigiKey Partnumber: " + str(response.json()['DigiKeyPartNumber']))
                #print(response.json())
                cost1 = "N/A"
                cost100 = "N/A"
                cost1000 = "N/A"
                for i in range(len(response.json()['StandardPricing'])):
                    #print(response.json()['StandardPricing'][i]['BreakQuantity'])
                    if response.json()['StandardPricing'][i]['BreakQuantity'] == 1:
                        cost1 = response.json()['StandardPricing'][i]['UnitPrice']
                        #print("Cost for 1: " + str(cost1))
                    if response.json()['StandardPricing'][i]['BreakQuantity'] == 100:
                        cost100 = response.json()['StandardPricing'][i]['UnitPrice']
                        #print("Cost for 100: " + str(cost100))
                    if response.json()['StandardPricing'][i]['BreakQuantity'] == 1000:
                        cost1000 = response.json()['StandardPricing'][i]['UnitPrice']
                        #print("Cost for 1000: " + str(cost1000))
                RoHS = 0   
                if(str(response.json()['RoHSStatus']) == "ROHS3 Compliant"):
                    RoHS = 1
                print(response.json())
                global newDataInfo
                if(response.json()['QuantityAvailable'] >0):
                    newDataInfo = (str(date.today()),"Got",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digi-Key',partnumber,  response.json()['Category']['Value'],cost1, cost100, cost1000, response.json()['QuantityAvailable'], response.json()['ProductDescription'],RoHS)
                else:
                    newDataInfo = (str(date.today()),"Potentially obsolete due to no available stock",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digi-Key',partnumber,  response.json()['Category']['Value'],cost1, cost100, cost1000, response.json()['QuantityAvailable'], response.json()['ProductDescription'],RoHS)

                #print(newDataInfo)
                return response_dict
            else:
                print(f'Failed to get information for {partnumber}')
                global failed
                failed = failed + 1
                print(response.status_code, response.reason)
                #newDataInfo = ('Failed', 'Failed', 'Failed', partnumber, 'Failed', 'Failed' )
                return False
            
        finally:
            # Close the connection
            connection.commit()
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    
def mouser_get_product_details(partnumber):
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            global misMatch
            #partnumber = quote(partnumber) #it replaces invalid characters in the partnumber
            url = f'https://api.mouser.com/api/v1/search/partnumber?apiKey={mouserKey}'
            url_data = {
                "SearchByPartRequest": {
                    "mouserPartNumber": partnumber
                }
            }
            url_headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.post(url, headers = url_headers, json=url_data)
            #print(response.json()['DigiKeyPartNumber'])
            if (response.status_code == 200):   
                if(response.json()['SearchResults']['NumberOfResult'] != 1):
                    print(f'Failed to get information for {partnumber}')
                    return False
                response_dict = response.json()
                if(partnumber != response.json()['SearchResults']["Parts"][0]['MouserPartNumber']):
                    misMatch = misMatch + 1
                    print("Mismatch Occured for "+partnumber +"/"+response.json()['SearchResults']["Parts"][0]['MouserPartNumber'] +" :Mouser Add")
                    return False
                print(f'Got information for {partnumber}')

                print("Manufacturer: " + str(response.json()['SearchResults']["Parts"][0]["Manufacturer"]))
                print("Available: " + str(response.json()['SearchResults']["Parts"][0]['AvailabilityInStock']))
                print("Category: " + str(response.json()['SearchResults']["Parts"][0]["Category"]))
                print("DigiKey Partnumber: " + str(response.json()['SearchResults']["Parts"][0]['MouserPartNumber']))
                #print(response.json())
                cost1 = "N/A"
                cost100 = "N/A"
                cost1000 = "N/A"
                for i in range(len(response.json()['SearchResults']["Parts"][0]["PriceBreaks"])):
                    if response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Quantity"] == 1:
                        cost1 = response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Price"].replace("$","")
                    if response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Quantity"] == 100:
                        cost100 = response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Price"].replace("$","")
                    if response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Quantity"] == 1000:
                        cost1000 = response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Price"].replace("$","")
                RoHS = 0
                if(str(response.json()['SearchResults']["Parts"][0]['ROHSStatus']) =="RoHS Compliant"):
                    RoHS = 1
                global newDataInfo
                if(str(response.json()['SearchResults']["Parts"][0]['AvailabilityInStock']) == "None"):
                    newDataInfo = (str(date.today()), "Potentially obsolete due to no available stock",response.json()['SearchResults']["Parts"][0]["Manufacturer"],response.json()['SearchResults']["Parts"][0]["ManufacturerPartNumber"], "Mouser", partnumber, response.json()['SearchResults']["Parts"][0]["Category"],cost1, cost100, cost1000,response.json()['SearchResults']["Parts"][0]['AvailabilityInStock'],response.json()['SearchResults']["Parts"][0]['Description'],RoHS)
                else:
                    newDataInfo = (str(date.today()), "Got",response.json()['SearchResults']["Parts"][0]["Manufacturer"],response.json()['SearchResults']["Parts"][0]["ManufacturerPartNumber"], "Mouser", partnumber, response.json()['SearchResults']["Parts"][0]["Category"],cost1, cost100, cost1000,response.json()['SearchResults']["Parts"][0]['AvailabilityInStock'],response.json()['SearchResults']["Parts"][0]['Description'],RoHS)
                #print(newDataInfo)
                return response_dict
            else:
                print(f'Failed to get information for {partnumber}')
                global failed
                failed = failed + 1
                print(response.status_code, response.reason)
                #newDataInfo = ('Failed', 'Failed', 'Failed', partnumber, 'Failed', 'Failed' )
                return False
            
        finally:
            # Close the connection
            connection.commit()
            connection.close()

    
def update_product_details(partnumber):
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            global misMatch
            #partnumber = quote(partnumber) #it replaces invalid characters in the partnumber
            partnumber = str(partnumber)
            url = f'https://api.digikey.com/Search/v3/Products/{partnumber}'
            token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
            query = "Select * FROM DigikeyValues"
            cursor.execute(query)
            for x in cursor:    
                tokenSQL = x     
            token['client_id'] = tokenSQL[0]
            token['client_secret'] = tokenSQL[1]
            token['access_token'] = tokenSQL[2]
            token['refresh_token'] = tokenSQL[3]
            token['expires_in'] = tokenSQL[4]
            token['refresh_token_expires_in'] = tokenSQL[5]
            token['token_type'] = tokenSQL[6]

            #print(url)
            #print(token['refresh_token'])
            #print(token['access_token'])
            url_header = {
                'x-digikey-locale': 'en',   
                'X-DIGIKEY-Locale-Site': 'US',
                'X-DIGIKEY-Locale-Currency': 'USD',
                'Authorization': f"{token['token_type']} {token['access_token']}",
                'X-DIGIKEY-Client-Id': token['client_id']
            }

            response = requests.get(url, headers=url_header)
            if(response.status_code == 401):
                use_refresh_token()
                token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
                query = "Select * FROM DigikeyValues"
                cursor.execute(query)
                for x in cursor:    
                    tokenSQL = x     
                token['client_id'] = tokenSQL[0]
                token['client_secret'] = tokenSQL[1]
                token['access_token'] = tokenSQL[2]
                token['refresh_token'] = tokenSQL[3]
                token['expires_in'] = tokenSQL[4]
                token['refresh_token_expires_in'] = tokenSQL[5]
                token['token_type'] = tokenSQL[6]
                url_header = {
                'x-digikey-locale': 'en',   
                'X-DIGIKEY-Locale-Site': 'US',
                'X-DIGIKEY-Locale-Currency': 'USD',
                'Authorization': f"{token['token_type']} {token['access_token']}",
                'X-DIGIKEY-Client-Id': token['client_id']
            }
                response = requests.get(url, headers=url_header)
            if (response.status_code == 200):      
                response_dict = response.json()
                if(partnumber != response.json()['DigiKeyPartNumber']):
                    misMatch = misMatch + 1
                    #cor = connection.cursor()
                    print("Mismatch occured for "+partnumber +"/"+response.json()['DigiKeyPartNumber']+" :Digi-Key Update")
                    print(response.json())
                    cursor.execute("SELECT `Manufacturer Part Number` FROM electronics_parts WHERE `Supplier Part Number 1` = '" + partnumber +"'")
                    manID = 0
                    for x in cursor:
                        manID = manID +1
                    manufact = ["Null"] * manID
                    manID = 0
                    cursor.execute("SELECT `Manufacturer Part Number` FROM electronics_parts WHERE `Supplier Part Number 1` = '" + partnumber +"'")
                    for x in cursor:
                        manufact[manID] = x
                        manID = manID+1
                    cleanMan = str(manufact[0]).replace("('","")                    #Cleans up the part numbers to make them just strings with no extra characters
                    cleanMan = cleanMan.replace("',)","")
                    if(cleanMan != response.json()['ManufacturerPartNumber']):
                        print("Mismatch occured for "+cleanMan+"/"+response.json()['ManufacturerPartNumber'])
                        return False
                    #cursor.execute("UPDATE electronics_parts SET Reason = %s WHERE `Supplier Part Number 1` = %s",("Potentially obsolete due to being unable to find part", partnumber))
                    #cursor.execute("UPDATE electronics_parts SET Updated = %s WHERE `Supplier Part Number 1` = %s",("No", partnumber))
                    #cor.execute("UPDATE electronics_parts SET Reason = %s WHERE `Supplier Part Number 1` = %s",("Potentially obsolete due to not being able to find part", partnumber))
                    #cor.execute("UPDATE electronics_parts SET Updated = %s WHERE `Supplier Part Number 1` = %s",("No", partnumber))
                print(f'Got information for {partnumber}')
                global gotten
                gotten = gotten + 1
                #print(response.json()['Manufacturer']['Value'])
                #print(response.json()['QuantityAvailable'])
                #print(response.json()['Category']['Value'])
                #print(response.json()['DigiKeyPartNumber'])
                #print(response.json())
                #print(len(response.json()['StandardPricing']))
                cost1 = "N/A"
                cost100 = "N/A"
                cost1000 = "N/A"
                for i in range(len(response.json()['StandardPricing'])):
                    #print(response.json()['StandardPricing'][i]['BreakQuantity'])
                    if response.json()['StandardPricing'][i]['BreakQuantity'] == 1:
                        cost1 = response.json()['StandardPricing'][i]['UnitPrice']
                    if response.json()['StandardPricing'][i]['BreakQuantity'] == 100:
                        cost100 = response.json()['StandardPricing'][i]['UnitPrice']
                    if response.json()['StandardPricing'][i]['BreakQuantity'] == 1000:
                        cost1000 = response.json()['StandardPricing'][i]['UnitPrice']
                #print(cost1)
                #print(cost100)
                #print(cost1000)
                RoHS = 0
                if(str(response.json()['RoHSStatus']) == "ROHS3 Compliant"):
                    RoHS = 1
                global newDataInfo  #Updated = %s, Reason = %s, Manufacturer = %s, Manufacturer_Part_Number = %s, Supplier = %s, Part_Category = %s, Cost_1pc = %s, Cost_100pc = %s, Cost_1000pc = %s, Stock = %s) WHERE Supplier_Part_Number = %s"
                if response.json()['QuantityAvailable'] != 0:
                    newDataInfo = (str(date.today()),"Got",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digi-Key',  response.json()['Category']['Value'],cost1, cost100, cost1000, response.json()['QuantityAvailable'],response.json()['ProductDescription'],RoHS,partnumber)
                else:
                    newDataInfo = (str(date.today()),"Potentially obsolete due to no available stock",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digi-Key',  response.json()['Category']['Value'],"0", "0", "0", response.json()['QuantityAvailable'],response.json()['ProductDescription'],RoHS,partnumber)

                #print(newDataInfo)
                connection.commit()
                print("Inside commit done: Digi-Key")
                return response_dict
            else:
                url = f'https://api.mouser.com/api/v1/search/partnumber?apiKey={mouserKey}'
                url_data = {
                    "SearchByPartRequest": {
                        "mouserPartNumber": partnumber
                    }
                }
                url_headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                response = requests.post(url, headers = url_headers, json=url_data)
                if (response.status_code == 200): 
                    if(response.json()['SearchResults']['NumberOfResult'] != 1):
                        print(f'Failed to get information for {partnumber}')
                        #cursor.execute("UPDATE electronics_parts SET Reason = %s WHERE `Supplier Part Number 1` = %s",("Potentially obsolete due to not being able to find part", partnumber))
                        #cursor.execute("UPDATE electronics_parts SET Updated = %s WHERE `Supplier Part Number 1` = %s",("No", partnumber))
                        return False
                    response_dict = response.json()
                    print(partnumber)
                    print(response.json())
                    if(partnumber != response.json()['SearchResults']["Parts"][0]['MouserPartNumber']):
                        misMatch = misMatch + 1
                        print("Mismatch Occured for "+partnumber +"/"+response.json()['SearchResults']["Parts"][0]['MouserPartNumber'] + " :Mouser Update")
                        #cursor.execute("UPDATE electronics_parts SET Reason = %s WHERE `Supplier Part Number 1` = %s",("Potentially obsolete due to not being able to find part", partnumber))
                        #cursor.execute("UPDATE electronics_parts SET Updated = %s WHERE `Supplier Part Number 1` = %s",("No", partnumber))
                        cursor.execute("SELECT `Manufacturer Part Number` FROM electronics_parts WHERE `Supplier Part Number 1` = '" + partnumber +"'")
                        manID = 0
                        for x in cursor:
                            manID = manID +1
                        manufact = ["Null"] * manID
                        manID = 0
                        cursor.execute("SELECT `Manufacturer Part Number` FROM electronics_parts WHERE `Supplier Part Number 1` = '" + partnumber +"'")
                        for x in cursor:
                            manufact[manID] = x
                            manID = manID+1
                        cleanMan = str(manufact[0]).replace("('","")                    #Cleans up the part numbers to make them just strings with no extra characters
                        cleanMan = cleanMan.replace("',)","")
                        if(cleanMan != response.json()['SearchResults']["Parts"][0]["ManufacturerPartNumber"]):
                            print("Mismatch occured for "+cleanMan+"/"+response.json()['SearchResults']["Parts"][0]["ManufacturerPartNumber"])
                            return False
                    print(f'Got information for {partnumber}')
                    cost1 = "N/A"
                    cost100 = "N/A"
                    cost1000 = "N/A"
                    for i in range(len(response.json()['SearchResults']["Parts"][0]["PriceBreaks"])):
                        if response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Quantity"] == 1:
                            cost1 = response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Price"].replace("$","")
                        if response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Quantity"] == 100:
                            cost100 = response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Price"].replace("$","")
                        if response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Quantity"] == 1000:
                            cost1000 = response.json()['SearchResults']["Parts"][0]["PriceBreaks"][i]["Price"].replace("$","")
                    RoHS = 0
                    if(str(response.json()['SearchResults']["Parts"][0]['ROHSStatus']) =="RoHS Compliant"):
                        RoHS = 1
                    if (str(response.json()['SearchResults']["Parts"][0]['AvailabilityInStock']) != "None"):
                        newDataInfo = (str(date.today()), "Got",response.json()['SearchResults']["Parts"][0]["Manufacturer"],response.json()['SearchResults']["Parts"][0]["ManufacturerPartNumber"], "Mouser", response.json()['SearchResults']["Parts"][0]["Category"],cost1, cost100, cost1000,response.json()['SearchResults']["Parts"][0]['AvailabilityInStock'],response.json()['SearchResults']["Parts"][0]['Description'],RoHS, partnumber)
                    else:
                        newDataInfo = (str(date.today()),"Potentially obsolete due to no available stock",response.json()['SearchResults']["Parts"][0]["Manufacturer"], response.json()['SearchResults']["Parts"][0]["ManufacturerPartNumber"], "Mouser",  response.json()['SearchResults']["Parts"][0]["Category"],"0", "0", "0", response.json()['SearchResults']["Parts"][0]['AvailabilityInStock'],response.json()['SearchResults']["Parts"][0]['Description'],RoHS,partnumber)
                    connection.commit()
                    print("Inside commit done: Mouser")
                    return response_dict
                else:
                    print(f'Failed to get information for {partnumber}')
                    #cursor.execute("UPDATE electronics_parts SET Reason = %s WHERE `Supplier Part Number 1` = %s",("Potentially obsolete due to being unable to find part", partnumber))
                    #cursor.execute("UPDATE electronics_parts SET Updated = %s WHERE `Supplier Part Number 1` = %s",("No", partnumber))
                    global failed
                    failed = failed + 1
                    print(response.status_code, response.reason)
                    #newDataInfo = ('Failed', 'Failed', 'Failed', partnumber, 'Failed', 'Failed' )
                    return False
                
        finally:
            # Close the connection
            connection.commit()
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    
    
#f = open("/Users/jamaa/Desktop/403python/digikey_token.json")
#holder = json.load(f)                                               #Holder holds the file information.
#print(holder)

"""
def ThreadUpdate():
    var = []
    lower = request.form['lower']       #lower bound, int
    lower = int(lower)
    upper = request.form['upper']       #upper bound, int
    upper = int(upper)
    for i in range(lower, upper):
        var.append(0)
        var[i-lower] = threading.Thread(target=Updating, args=(i,i+1))
        var[i-lower].start()
        print("Variable" + str(i-lower) + "Started")
    for i in range(lower, upper):
        var[i-lower].join()
        print("Variable" + str(i-lower) + "Finished")
    return("Update function done")
"""    
@app.route('/Update', methods = ['POST'])
def Updating():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            failedData= ("","","")
            lower = request.form['lower']       #lower bound, int
            lower = int(lower)
            upper = request.form['upper']       #upper bound, int
            upper = int(upper)
            query = "SELECT `Supplier Part Number 1` FROM electronics_parts WHERE ID>="+str(lower)+" and ID<="+str(upper)+" ORDER BY CASE WHEN `ID` > 0 THEN 0 ELSE 1 END, `ID`"
            cursor.execute(query)
            id = 0             #Loads the current part numbers into a list
            for x in cursor:
                id = id+1       #Counts the number of partnumbers within the table
            datanumbers = ['null'] * id     #Intitalzies a list based on that number
            id = 0
            cursor.execute(query)
            for x in cursor:    
                datanumbers[id] = x     #Puts the partnumber into the list
                id = id+1
            if(id<1):
                return "ERROR: No parts found. Check Bounds"
            for i in range(id):                                               #Loops through the database and checks the part numbers
                clean = str(datanumbers[i]).replace("('","")                    #Cleans up the part numbers to make them just strings with no extra characters
                clean = clean.replace("',)","")
                if(checkDup(clean)):
                    global alrExist 
                    alrExist = alrExist +1
                    updateProd = update_product_details(clean)
                    if(updateProd != False):
                        cursor.execute(update_info, newDataInfo)
                    else:
                        failedData = ("No", "Potentially obsolete due to being unable to find part", clean)
                        cursor.execute(update_failed, failedData)
                else:
                    print("Part can not be found in database")
            connection.commit()
            print("Final Commit")
            return("Update function done")
        finally:
            # Close the connection
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    
@app.route('/Add', methods = ['POST'])
def Adding():
    with sshtunnel.SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USERNAME,
        ssh_password=SSH_PASSWORD,  # or ssh_pkey=SSH_PKEY
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT)
    ) as tunnel:
        # Connect to MySQL through the tunnel
        connection = pymysql.connect(
            host='127.0.0.1',  # Connect to the local end of the tunnel
            port=tunnel.local_bind_port,
            user=MYSQL_USERNAME,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        try:
            cursor = connection.cursor()
            toAdd = request.form['partnumber']      #Partnumber the use wants to add
            supplier = request.form.get('supplier',"Both")
            if(checkDup(toAdd)):
                print("Part already exists")
                return("Part already exists")
            else:
                if(supplier == "Digi-Key"):
                    plug = get_product_details(toAdd)           #493-4330-ND
                    if(plug != False):
                        cursor.execute(add_info, newDataInfo)
                        cursor.execute("SELECT TestID FROM electronics_parts WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                        holderID = 0
                        hold = ['null']*3
                        for x in cursor:
                            x = str(x).replace("(","")                    #Cleans up the part numbers to make them just strings with no extra characters
                            x = x.replace(",)","")
                            holderID = int(x) + 50
                        cursor.execute("UPDATE electronics_parts SET ID = "+str(holderID)+" WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                        return("Info added via Digi-Key")
                    else:
                        return "Part not found, ensure you are using the Digikey partnumber."
                elif(supplier == "Mouser"):
                    plug = mouser_get_product_details(toAdd)
                    if(plug != False):
                        cursor.execute(add_info, newDataInfo)
                        cursor.execute("SELECT TestID FROM electronics_parts WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                        holderID = 0
                        hold = ['null']*3
                        for x in cursor:
                            x = str(x).replace("(","")                    #Cleans up the part numbers to make them just strings with no extra characters
                            x = x.replace(",)","")
                            holderID = int(x) + 50
                        cursor.execute("UPDATE electronics_parts SET ID = "+str(holderID)+" WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                        return("Info added via Mouser")
                    else:
                        return "Part not found, ensure you are using the Mouser partnumber."
                else:
                    plug = get_product_details(toAdd)           #493-4330-ND
                    if(plug != False):
                        cursor.execute(add_info, newDataInfo)
                        cursor.execute("SELECT TestID FROM electronics_parts WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                        holderID = 0
                        for x in cursor:
                            x = str(x).replace("(","")                    #Cleans up the part numbers to make them just strings with no extra characters
                            x = x.replace(",)","")
                            holderID = int(x) + 50
                        cursor.execute("UPDATE electronics_parts SET ID = "+str(holderID)+" WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                        return("Info first added via Digi-Key")
                    else:
                        plug = mouser_get_product_details(toAdd)
                        if(plug != False):
                            cursor.execute(add_info, newDataInfo)
                            cursor.execute("SELECT TestID FROM electronics_parts WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                            holderID = 0
                            for x in cursor:
                                x = str(x).replace("(","")                    #Cleans up the part numbers to make them just strings with no extra characters
                                x = x.replace(",)","")
                                holderID = int(x) + 50
                            cursor.execute("UPDATE electronics_parts SET ID = "+str(holderID)+" WHERE `Supplier Part Number 1` = '"+toAdd+"'")
                            return("Info first added via Mouser")
                        else:
                            return "Part not found, ensure you are using the a valid partnumber."
            #connection.commit()
        finally:
            # Close the connection
            connection.commit()
            connection.close()
    #conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    
#get_product_details("493-4330-ND",holder)
"""choice = int(input("1 for filter, 2 for sort, 3 for add tag, 4 for Updating a range, 5 for add part: "))
if choice == 1:
    Filtering()
elif choice == 2:
    Sorting()
elif choice == 3:
    Tagging()
elif choice == 4:
    Updating()
elif choice ==5:
    Adding()
else:
    use_refresh_token()"""
print(str(gotten) + " gotten")
print(str(failed) + " failed")
#print(str(alrExist) + " already exist")
print(str(misMatch) + " Mismatches occured")
#f.close()


if __name__ == "__main__":
   app.run()
