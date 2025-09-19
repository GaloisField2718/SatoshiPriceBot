from fetch_prices import CoinDataFetcher

 # To convert sats to btc way=0, to convert btc to sats it's 1.
def satsbtc(amount, way):
     if way == 0:
         btc = amount/(10**8)
         btc = round(btc, 8)
         return btc
     elif way == 1:
         amount = round(amount,8)
         sats = amount*(10**8)
         sats = int(sats)
         return sats
     else : 
         return "Enter 0 or 1."

# To convert btc to eur way = 0, to convert eur to btc it's 1
def btceur(amount, way):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)
    price = fetcher.get_current_price(market_data, "eur")

    if way == 0:
        eur_price = price*amount
        eur_price = round(eur_price,3)
        return eur_price
    elif way == 1:
        btc = amount/price
        btc = round(btc,8)
        return btc
    else : 
        return "Enter 0 or 1."
    
# To convert btc to usd way = 0, to convert usd to btc it's 1
def btcusd(amount, way):
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)
    price = fetcher.get_current_price(market_data, "usd")
    if way == 0:
        usd_price = price * amount
        usd_price = round(usd_price, 3)
        return usd_price
    elif way == 1:
        btc = amount / price
        btc = round(btc, 8)
        return btc
    else:
        return "Enter 0 or 1."

# sats-> eur : way = 0, eur-> sats : way = 1
def satseur(amount,way):
    if way == 0:
        eur = btceur(satsbtc(amount,0),0)
        eur = round(eur,3)
        return eur
    elif way == 1:
        sats = satsbtc(btceur(amount,1),1)
        sats = int(sats)
        return sats
    else : 
        return "Enter 0 or 1."

# sats -> usd : way = 0, usd -> sats : way = 1
def satsusd(amount, way):
    if way == 0:
        usd = btcusd(satsbtc(amount, 0), 0)
        usd = round(usd, 3)
        return usd
    elif way == 1:
        sats = satsbtc(btcusd(amount, 1), 1)
        sats = int(sats)
        return sats
    else:
        return "Enter 0 or 1."

