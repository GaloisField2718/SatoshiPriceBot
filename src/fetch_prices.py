import requests
import json
import pprint


url = "https://api.coingecko.com/api/v3/coins/bitcoin"
params = {
        "localization":"fr",
        "tickers": "true",
        "market_data":"true",
        "community_data":"true"
        } 

response = requests.get(url,params)

data = json.loads(response.text)

description = data["description"]["sl"]
genesis = data["genesis_date"]

market_data = data["market_data"]

price = data["market_data"]["current_price"]["eur"] 

ath = market_data["ath"]["eur"]

change_from_ath = market_data["ath_change_percentage"]["eur"]

ath_date = market_data["ath_date"]["eur"]

fully_diluted_valuation = market_data["fully_diluted_valuation"]["eur"]

fully_diluted_valuation = "{:=,}".format(fully_diluted_valuation)


percent_change_1h = market_data["price_change_percentage_1h_in_currency"]["eur"]
percent_change_24h = market_data["price_change_percentage_24h_in_currency"]["eur"]
percent_change_7d = market_data["price_change_percentage_7d_in_currency"]["eur"]
percent_change_14d = market_data["price_change_percentage_14d_in_currency"]["eur"]
percent_change_30d = market_data["price_change_percentage_30d_in_currency"]["eur"]
percent_change_200d = market_data["price_change_percentage_200d_in_currency"]["eur"]
percent_change_1y = market_data["price_change_percentage_1y_in_currency"]["eur"]

actual_supply = market_data["circulating_supply"]

timestamp = market_data["last_updated"]

dev_data = data["developer_data"]


forks = dev_data["forks"]
stars = dev_data["stars"]
subs = dev_data["subscribers"]
total_issues = dev_data["total_issues"]
pull_requests = dev_data["pull_requests_merged"]
contributors = dev_data["pull_request_contributors"]
additions_deletions = dev_data["code_additions_deletions_4_weeks"] #{ "additions": 4932,"deletions": -1770}
commit_4w = dev_data["commit_count_4_weeks"]

public = data["public_interest_stats"]


# Compute 5 major exchange in volume

tickers = data["tickers"]

number_exchanges = len(tickers)
all_volumes_dict = []

for exchange in range(number_exchanges):
    pair = f"{tickers[exchange]['base']}/{ tickers[exchange]['target']}"
    infos = {"exchange": tickers[exchange]["market"]["name"], "volume" : tickers[exchange]["volume"], "coin gecko score" : tickers[exchange]["trust_score"], "last trade": tickers[exchange]["last_traded_at"], "url" : tickers[exchange]["trade_url"], "pair" : pair}
    
    all_volumes_dict.append(infos)


all_volumes_sorted = sorted(all_volumes_dict, key=lambda x:x["volume"], reverse=True)


#print("\n ------------------- FIVE MAJORS VOLUME ---------------- \n ")

major_volumes = [all_volumes_sorted[index] for index in range(5)]


#major_exchanges = [major_volumes[index][index] for index in range(5)]

#pprint.pprint(major_volumes)

#print("Five major exchange : ", major_exchanges)

#print("\n -------------------- KRAKEN ------------------------ \n ")

indices_kraken = [i for i, item in enumerate(all_volumes_dict) if item["exchange"] == "Kraken"]
kraken = [all_volumes_dict[index] for index in indices_kraken]

#pprint.pprint(kraken)

#print("\n ----------------------------- BINANCE -------------------- \n")

indices_binance = [i for i, item in enumerate(all_volumes_dict) if item["exchange"] == "Binance"]
binance = [all_volumes_dict[index] for index in indices_binance]

#pprint.pprint(binance)




