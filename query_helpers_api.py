import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://404-app-integration.vercel.app"
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN") or "YOUR_STATIC_TOKEN_HERE"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def add_part(part_number):
    url = f"{API_BASE_URL}/Add"
    data = {"partnumber": part_number}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()

def filter_parts(category, value):
    url = f"{API_BASE_URL}/Filter"
    data = {"category": category, "value": value}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()

def sort_parts(category):
    url = f"{API_BASE_URL}/Sort"
    data = {"category": category}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()

def tag_part(part_number, tag):
    url = f"{API_BASE_URL}/Tag"
    data = {"partnumber": part_number, "tag": tag}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()

def update_part(part_number, updated_info):
    url = f"{API_BASE_URL}/Update"
    data = {"partnumber": part_number, **updated_info}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()

def delete_part(part_number):
    url = f"{API_BASE_URL}/Delete"
    data = {"partnumber": part_number}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()

def get_limitby_options(category):
    url = f"{API_BASE_URL}/limitby"
    data = {"category": category}
    response = requests.post(url, data=data, headers=HEADERS)
    return response.json()
