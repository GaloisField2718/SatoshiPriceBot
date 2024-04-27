import requests
import json
from pprint import pprint


url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30'

params ={
        "total_volumes": "false",
        "prices" : "false"
        }

response = requests.get(url, params=params)


data = json.loads(response.text)

pprint(data)
