# Fetch coin data
import requests
import json
from datetime import datetime

class CoinDataFetcher :

  def __init__(self, coin_id):
    self.coin_id = coin_id

  # Fetch coin data
  def get_coin_data(self):
    url = f"https://api.coingecko.com/api/v3/coins/{self.coin_id}"
    params = {
      "localization":"fr",  
      "tickers":"true",
      "market_data":"true",
      "community_data":"true"
    }

    response = requests.get(url, params=params)
    return json.loads(response.text)

  # Get description
  def get_description(self, data):
    return data["description"]["en"]

  # Get genesis date
  def get_genesis_date(self, data):
    return data["genesis_date"]

  # Get market data
  def get_market_data(self, data):
    return data["market_data"]

  # Get current price
  def get_current_price(self, market_data):
    return market_data["current_price"]["eur"]
  
# Get current timestamp
  def get_timestamp(self, market_data):
      return market_data["last_updated"]

  # Get ATH details
  def get_ath_data(self, market_data):
    return {
      "ath": market_data["ath"]["eur"],
      "ath_change": market_data["ath_change_percentage"]["eur"],
      "ath_date": market_data["ath_date"]["eur"]
    }

  # Get fully diluted valuation
  def get_fdv(self, market_data):
    return market_data["fully_diluted_valuation"]["eur"]  

  # Get percentage changes
  def get_percentage_changes(self, market_data):
    return {
      "1h": market_data["price_change_percentage_1h_in_currency"]["eur"],
      "24h": market_data["price_change_percentage_24h_in_currency"]["eur"],
      "7d": market_data["price_change_percentage_7d_in_currency"]["eur"],
      "14d":market_data["price_change_percentage_14d_in_currency"]["eur"],
      "30d":market_data["price_change_percentage_30d_in_currency"]["eur"],
      "200d":market_data["price_change_percentage_200d_in_currency"]["eur"],
      "1y":market_data["price_change_percentage_1y_in_currency"]["eur"],
    }

  # Get circulating supply
  def get_circulating_supply(self, market_data):
    return market_data["circulating_supply"]

  # Get last updated
  def get_last_updated(self, market_data):
    return market_data["last_updated"]

  # Get developer data
  def get_dev_data(self, data):
    return data["developer_data"]
  
  def get_public(self, data):
      return data["public_interest_stats"]

  def get_tickers(self, data):
    return data['tickers']

  # Get exchange volumes
#  def get_exchange_volumes(self, tickers):
#    volumes = []
#    for t in tickers:
#      pair = f"{t['base']}/{t['target']}"
#      volume = {
#        "exchange": t["market"]["name"], 
#        "volume": t["volume"],
#        "pair": pair
#      }
#      volumes.append(volume)
#    return volumes

  def get_all_volumes(self, tickers):
    volumes = []
    for t in tickers:
        pair = f"{t['base']}/{t['target']}"
        volume = {
                "exchange": t["market"]["name"],
                "volume": t["volume"], 
                "trust_score": t["trust_score"],
                "last_trade": t["last_traded_at"],
                "url": t["trade_url"],
                "pair": pair
                }
        volumes.append(volume)
    return volumes
  
  def get_major_volumes(self, all_volumes):
    sorted_volumes = sorted(all_volumes, key=lambda x: x["volume"], reverse=True)
    return sorted_volumes[:5]

  def get_kraken_volumes(self, all_volumes):
    return [v for v in all_volumes if v["exchange"] == "Kraken"]
  
  def get_binance_volumes(self, all_volumes):
    return [v for v in all_volumes if v["exchange"] == "Binance"]

# Usage
coin_id = "bitcoin"
fetcher = CoinDataFetcher(coin_id)
data = fetcher.get_coin_data()
description = fetcher.get_description(data)
market_data = data["market_data"]
timestamp = fetcher.get_timestamp(market_data)
print("At ", timestamp, "    ",description)
