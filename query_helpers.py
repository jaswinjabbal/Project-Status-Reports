# query_helpers.py — Modularized Helper Functions for Filtering, Sorting, Tagging, Digikey Integration

from urllib.parse import quote
import requests
import json


def use_refresh_token(token_path):
    with open(token_path) as f:
        token = json.load(f)

    url = 'https://api.digikey.com/v1/oauth2/token'
    url_data = {
        'refresh_token': token['refresh_token'],
        'client_id': token['client_id'],
        'client_secret': token['client_secret'],
        'redirect_uri': 'https://localhost',
        'grant_type': 'refresh_token'
    }

    response = requests.post(url, data=url_data)

    if response.status_code == 200:
        data = response.json()
        token.update({
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expires_in': data['expires_in'],
            'refresh_token_expires_in': data['refresh_token_expires_in'],
            'token_type': data['token_type']
        })
        with open(token_path, 'w') as f:
            json.dump(token, f)
    return token


def filter_parts(cursor, category, value, limit, offset):
    query = f"SELECT * FROM partInfo WHERE `{category}` = %s LIMIT %s OFFSET %s"
    cursor.execute(query, (value, limit, offset))
    return cursor.fetchall()


def count_filtered_parts(cursor, category, value):
    query = f"SELECT COUNT(*) as total FROM partInfo WHERE `{category}` = %s"
    cursor.execute(query, (value,))
    return cursor.fetchone()['total']


def sort_parts(cursor, category, limit, offset):
    query = f"SELECT * FROM partInfo ORDER BY `{category}` LIMIT %s OFFSET %s"
    cursor.execute(query, (limit, offset))
    return cursor.fetchall()


def tag_part(cursor, part_number, tag_value):
    cursor.execute("SELECT Tags FROM partInfo WHERE Supplier_Part_Number = %s", (part_number,))
    result = cursor.fetchone()
    prev_tag = result[0] if result else '0'
    new_tag = tag_value if prev_tag == '0' else f"{prev_tag}, {tag_value}"
    cursor.execute("UPDATE partInfo SET Tags = %s WHERE Supplier_Part_Number = %s", (new_tag, part_number))


def get_product_details(partnumber, token):
    partnumber = quote(partnumber)
    url = f'https://api.digikey.com/Search/v3/Products/{partnumber}'
    headers = {
        'x-digikey-locale': 'en',
        'X-DIGIKEY-Locale-Site': 'US',
        'X-DIGIKEY-Locale-Currency': 'USD',
        'Authorization': f"{token['token_type']} {token['access_token']}",
        'X-DIGIKEY-Client-Id': token['client_id']
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        return None
    return response.json() if response.status_code == 200 else None


def insert_part(cursor, product):
    cost1, cost100, cost1000 = "N/A", "N/A", "N/A"
    for p in product.get('StandardPricing', []):
        if p['BreakQuantity'] == 1:
            cost1 = p['UnitPrice']
        elif p['BreakQuantity'] == 100:
            cost100 = p['UnitPrice']
        elif p['BreakQuantity'] == 1000:
            cost1000 = p['UnitPrice']

    values = (
        "Yes", "Got",
        product['Manufacturer']['Value'],
        product['ManufacturerPartNumber'],
        "Digikey",
        product['DigiKeyPartNumber'],
        product['Category']['Value'],
        cost1, cost100, cost1000,
        product['QuantityAvailable']
    )

    query = ("INSERT INTO partInfo (Updated, Reason, Manufacturer, Manufacturer_Part_Number, Supplier, "
             "Supplier_Part_Number, Part_Category, Cost_1pc, Cost_100pc, Cost_1000pc, Stock)"
             " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(query, values)


def get_distinct_values(cursor, column):
    query = f"SELECT DISTINCT `{column}` FROM partInfo"
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall() if row[0]]
