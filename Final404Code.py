from __future__ import print_function       #Imports necessary to use
import requests
import json
import time
import sys
from urllib.parse import quote
import mysql.connector
from mysql.connector import errorcode

from flask import Flask, request


tempCode = 'LJkkcWmQ'                   #Used when refresh token fails, intializes value
#token_filename = 'digikey_token.json'   #File containing neccesary values  Obsolete
#Dir = "/Users/jamaa/Desktop/403python/" #Directory where code is stored

app = Flask(__name__)

@app.route('/')
def base():
    return("Default")

@app.route('/refreshToken')
def use_refresh_token():
    token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
    cnx = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")      #Currently connect to local database
    query = "Select * FROM DigikeyValues"
    cursor = cnx.cursor()
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
        cursor.execute(queryRefresh, refreshDataInfo)
        cnx.commit()
        cnx.close()
    else:       #If failed
        print("Go to https://api.digikey.com/v1/oauth2/authorize?response_type=code&client_id=7nuAFcFkxQANPZevGdx00G4i0rw9gfTg&redirect_uri=https://localhost and gather the Auth code")
        #Must first get the authorization code from the given url. 
        tempCode = str(input("Enter the auth code"))
        get_access_token(tempCode)   
   # with open(Dir+token_filename, "w") as f:
    #    json.dump(token, f)
    return("Refresh Token called")

def get_access_token(auth_code):
    token = {"client_id": "", "client_secret": "", "access_token": "", "refresh_token": "", "expires_in": "", "refresh_token_expires_in": "", "token_type": ""}
    cnx = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")      #Currently connect to local database
    query = "Select * FROM DigikeyValues"
    cursor = cnx.cursor()
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
        cnx.commit()
        cnx.close()
    return(response.json())
    
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

conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
cursor = conn.cursor()
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
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    filter = request.form['filter']     #What category are you filtering by. Ex. Manufacturer
    #print(filter)
    limitby = request.form['limitby']   #What value do you want to see. Ex. Texas Instruments
    filterQuery = "SELECT * FROM partInfo WHERE "+filter+" = '"+limitby+"'"
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

@app.route('/Sort', methods = ['POST'])
def Sorting():
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    sort = request.form['sort']     #What category do you want sorted. Ex. Manufacturer
    #print(sort)
    sortQuery = "SELECT * FROM partInfo ORDER BY "+sort
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




@app.route('/Tag', methods = ['POST'])
def Tagging():
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    prevTag = 0
    updateTag = "UPDATE partInfo SET Tags = %s WHERE Supplier_Part_Number = %s" 
    upVals = ("1","2")      #1 is the tag while 2 is the partnumber
    tagPart = request.form['partnumber']        #Partnumber where you want to add a tag
    tagValue = request.form['tag']              #What the tag should be
    tagQuery = "SELECT Tags FROM partInfo WHERE Supplier_Part_Number = '"+tagPart+"'"
    cursor.execute(tagQuery)
    for x in cursor:
        prevTag = x
    prevTag = str(prevTag).replace("('","")                    #Makes the previous tag a normal string with no extra characters
    prevTag = prevTag.replace("',)","")
    #print(prevTag)
    if prevTag == "0":
        upVals = (tagValue, tagPart)
    else:
        upVals = (prevTag+", "+tagValue, tagPart)
    cursor.execute(updateTag, upVals)
    conn.commit()
    return("Tag Added")

@app.route('/Delete', methods=['POST'])
def Deleting():
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    delCat = request.form['category']   #Category, you will have to default it to supplier_partnumber
    delVal = request.form['delete']     #Partnumber of what you want to delete
    delQuery = "DELETE FROM partInfo WHERE " + delCat + " = '"+delVal+"'"
    cursor.execute(delQuery)
    conn.commit()
    return("Part deleted")

add_info = ("INSERT INTO partInfo "
            "(Updated, Reason, Manufacturer, Manufacturer_Part_Number, Supplier, Supplier_Part_Number, Part_Category, Cost_1pc, Cost_100pc, Cost_1000pc, Stock)"
            "VALUES(%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)")
update_info = ("UPDATE partInfo SET Updated = %s, Reason = %s, Manufacturer = %s, Manufacturer_Part_Number = %s, Supplier = %s, Part_Category = %s, Cost_1pc = %s, Cost_100pc = %s, Cost_1000pc = %s, Stock = %s WHERE Supplier_Part_Number = %s")

def checkDup(partnumber):
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
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

    #print(partnumber + " Is the partnumber")
    for x in range(len(datanumbers)):
        clean = str(datanumbers[x]).replace("('","")                    #Cleans up the part numbers to make them just strings with no extra characters
        clean = clean.replace("',)","")
        #print(clean)
        if(partnumber == clean):
            return True                 #"Part Already Exists in database"
    return False
    

def get_product_details(partnumber):
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    global misMatch
    partnumber = quote(partnumber) #it replaces invalid characters in the partnumber
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
            print("MisMatch Occured for "+partnumber +"/"+response.json()['DigiKeyPartNumber'])
            return False
        print(f'Got information for {partnumber}')
        global gotten
        gotten = gotten + 1
        print("Manufacturer: " + str(response.json()['Manufacturer']['Value']))
        print("Available: " + str(response.json()['QuantityAvailable']))
        print("Category: " + str(response.json()['Category']['Value']))
        print("DigiKey Partnumber: " + str(response.json()['DigiKeyPartNumber']))
        #print(response.json())
        cost1 = "N/A"
        cost100 = "N/A"
        cost1000 = "N/A"
        for i in range(len(response.json()['StandardPricing'])):
            #print(response.json()['StandardPricing'][i]['BreakQuantity'])
            if response.json()['StandardPricing'][i]['BreakQuantity'] == 1:
                cost1 = response.json()['StandardPricing'][i]['UnitPrice']
                print("Cost for 1: " + str(cost1))
            if response.json()['StandardPricing'][i]['BreakQuantity'] == 100:
                cost100 = response.json()['StandardPricing'][i]['UnitPrice']
                print("Cost for 100: " + str(cost100))
            if response.json()['StandardPricing'][i]['BreakQuantity'] == 1000:
                cost1000 = response.json()['StandardPricing'][i]['UnitPrice']
                print("Cost for 1000: " + str(cost1000))
        global newDataInfo
        newDataInfo = ("Yes","Got",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digikey',partnumber,  response.json()['Category']['Value'],cost1, cost100, cost1000, response.json()['QuantityAvailable'])
        #print(newDataInfo)
        return response_dict
    else:
        print(f'Failed to get information for {partnumber}')
        global failed
        failed = failed + 1
        print(response.status_code, response.reason)
        #newDataInfo = ('Failed', 'Failed', 'Failed', partnumber, 'Failed', 'Failed' )
        return False
    
def update_product_details(partnumber):
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    global misMatch
    partnumber = quote(partnumber) #it replaces invalid characters in the partnumber
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
    print(token['refresh_token'])
    print(token['access_token'])
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
            print("MisMatch Occured for "+partnumber +"/"+response.json()['DigiKeyPartNumber'])
            cursor.execute("UPDATE partInfo SET Reason = %s WHERE Supplier_Part_Number = %s",("Potentially Obsolete", partnumber))
            return False
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
        global newDataInfo  #Updated = %s, Reason = %s, Manufacturer = %s, Manufacturer_Part_Number = %s, Supplier = %s, Part_Category = %s, Cost_1pc = %s, Cost_100pc = %s, Cost_1000pc = %s, Stock = %s) WHERE Supplier_Part_Number = %s"
        if response.json()['QuantityAvailable'] != 0:
            newDataInfo = ("Yes","Got",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digikey',  response.json()['Category']['Value'],cost1, cost100, cost1000, response.json()['QuantityAvailable'],partnumber)
        else:
            newDataInfo = ("Yes","Potentially Obsolete",response.json()['Manufacturer']['Value'], response.json()['ManufacturerPartNumber'], 'Digi-key',  response.json()['Category']['Value'],"0", "0", "0", response.json()['QuantityAvailable'],partnumber)

        #print(newDataInfo)
        return response_dict
    else:
        print(f'Failed to get information for {partnumber}')
        cursor.execute("UPDATE partInfo SET Reason = %s WHERE Supplier_Part_Number = %s",("Potentially Obsolete", partnumber))
        global failed
        failed = failed + 1
        print(response.status_code, response.reason)
        #newDataInfo = ('Failed', 'Failed', 'Failed', partnumber, 'Failed', 'Failed' )
        return False
    
#f = open("/Users/jamaa/Desktop/403python/digikey_token.json")
#holder = json.load(f)                                               #Holder holds the file information.
#print(holder)
@app.route('/Update', methods = ['POST'])
def Updating():
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
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
    lower = request.form['lower']       #lower bound, int
    upper = request.form['upper']       #upper bound, int
    for i in range(lower, upper):                                               #Loops through the database and checks the part numbers
        clean = str(datanumbers[i]).replace("('","")                    #Cleans up the part numbers to make them just strings with no extra characters
        clean = clean.replace("',)","")
        if(checkDup(clean)):
            global alrExist 
            alrExist = alrExist +1
            updateProd = update_product_details(clean)
            if(updateProd != False):
                cursor.execute(update_info, newDataInfo)
        else:
            print("Part can not be found in database")
    conn.commit()
    return("Done")
@app.route('/Add', methods = ['POST'])
def Adding():
    conn = mysql.connector.connect(host = 'partsdatabase.cp06e0uayi8r.us-east-2.rds.amazonaws.com', password = 'F79BDG.4MkdA-dX', user = 'admin', database = "lusherengineeringpartsdatabase")
    cursor = conn.cursor()
    toAdd = request.form['partnumber']      #Partnumber the use wants to add
    if(checkDup(toAdd)):
        print("Part already exists")
        return("Part already exists")
    else:
        plug = get_product_details(toAdd)           #493-4330-ND
        if(plug != False):
                cursor.execute(add_info, newDataInfo)
    conn.commit()
    return("Info added")
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
conn.commit()
cursor.close()
conn.close()

if __name__ == "__main__":
   app.run()