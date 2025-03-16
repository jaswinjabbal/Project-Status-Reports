from __future__ import print_function       #Imports necessary to use
import requests
import json
import time
import sys
from urllib.parse import quote

def Add():
    url = 'https://404-app-integration.vercel.app/Add'
    headers = {"Authorization" : "Bearer iWtZuwF0U3wwxs4U4Jfm8Z6b"}
    data = {'partnumber': '1N4448XTPMSCT-ND'}           #Partnumber to be added, Currently needs to be supplier part number and specifaclly cut and reel if there is an option
    response = requests.post(url, data=data, headers=headers)
    return(response.text)

def Tag():
    url = 'https://404-app-integration.vercel.app/Tag'
    headers = {"Authorization" : "Bearer iWtZuwF0U3wwxs4U4Jfm8Z6b"}
    data = {'partnumber': '1N4448XTPMSCT-ND',       #Partnumber where tag is to be added
            'tag' : "Test 4"}                       #Tag to be added
    response = requests.post(url, data=data, headers=headers)
    return(response.text)

def Update():
    url = 'https://404-app-integration.vercel.app/Update'
    headers = {"Authorization" : "Bearer iWtZuwF0U3wwxs4U4Jfm8Z6b"}
    data = {'lower' : '0',                      #lower bound
            'upper' : '10'}                     #upper bound, Recommended don't do more then like 10 as it may time out
    response = requests.post(url, data=data, headers=headers)
    return(response.text)

def Delete():
    url = 'https://404-app-integration.vercel.app/Delete'
    headers = {"Authorization" : "Bearer iWtZuwF0U3wwxs4U4Jfm8Z6b"}
    data = {'category': 'Supplier_Part_Number', #Propably just default to supplier part number
            'delete': '1N4448XTPMSCT-ND'}       #Part number to be deleted
    response = requests.post(url, data=data, headers=headers)
    return(response.text)

def Sort():
    url = 'https://404-app-integration.vercel.app/Sort'
    headers = {"Authorization" : "Bearer iWtZuwF0U3wwxs4U4Jfm8Z6b"}
    data ={'sort': 'Updated'}                   #What column is going to be sorted
    response = requests.post(url, data=data, headers=headers)
    return(response.json())

def Filter():
    url = 'https://404-app-integration.vercel.app/Filter'
    headers = {"Authorization" : "Bearer iWtZuwF0U3wwxs4U4Jfm8Z6b"}
    data ={'filter': 'Updated',                 #In what category are you looking for a value 
           'limitby' : 'Yes'}                   #What value are you looking for
    response = requests.post(url, data=data, headers=headers)
    return(response.json())

print(Sort())