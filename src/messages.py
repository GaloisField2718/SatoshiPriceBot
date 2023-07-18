from fetch_prices import *
from datetime import datetime, timedelta, timezone
import convert

# Time management
date_str = timestamp
date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
# Convertir la date en fuseau horaire UTC+2
date = date.astimezone(timezone(timedelta(hours=2)))


# utils function
def convert_str(data):
    printable_str = str(data).replace("{", "").replace("}", "")
    return printable_str

def display_format(major_volumes):
    major_volumes_str = ""
    for index in range(len(major_volumes)):
        if index != len(major_volumes)-1:
            major_volumes_str += f"- {convert_str(major_volumes[index])} ; \n "
        else : 
            major_volumes_str += f"- {convert_str(major_volumes[index])}.\n"

    return major_volumes_str

# Formattage

actual_supply_str = "{:=,}".format(actual_supply)
price_str = "{:=,}".format(price)
ath_str = "{:=,}".format(ath)

# Messages

## General information
message_price = f"At {date} (Paris timezone) : 1 BTC = {price_str} EUR. \n"
message_ath = f"Bitcoin All Time High (ATH) was {ath_str} EUR at {ath_date}. Since ATH, Bitcoin dropped by : {change_from_ath}%.\n"

message_change = f"Bitcoin movements against Euro 💶 : \n - In 1 hour Bitcoin moves : {percent_change_1h}% ;\n - In 24 hours : {percent_change_24h}% ;\n - In 7 days : {percent_change_7d}% ; \n - In 30 days : {percent_change_30d}% ;\n - In 200 days : {percent_change_200d}% ;\n - In 1 year : {percent_change_1y}%.\n"

message_supply = f"Actual supply of Bitcoin is {actual_supply_str} BTC, for a fully diluted market cap : {fully_diluted_valuation} EUR. \n "

message_dev = f"From Github repo (https://github.com/bitcoin/bitcoin) we have : \n - {forks} forks ; \n  - {stars} stars ; \n - {subs} subscribers ; \n - {total_issues} total issues reported ; \n {pull_requests} pull requests to merge ; \n - {contributors} contributors ; \n - {additions_deletions['additions']} additions for {additions_deletions['deletions']} deletions ; \n - {commit_4w} commits on last 4 weeks.\n"

message_public = f"A simple measure of interest took from coingecko : {public}.\n"

message_info = f"Bitcoin was born {genesis}, it can be described as like this :\n {description}\n {message_ath}\n {message_supply}\n For more information take a look on informative commands.\n"



## Volume data

### Major volumes
header_major_volumes = "👉  5 MOST TRADED PAIRS WITH EXCHANGE  👈 "
major_volumes_str = display_format(major_volumes)
message_major_volumes = f"{header_major_volumes}\n\n {major_volumes_str} \n"

### Kraken volumes
header_kraken = "👉  KRAKEN TRADES BTC  👈"
kraken_volumes = display_format(kraken)
message_kraken = f"{header_kraken} \n \n {kraken_volumes}\n"

### Binance volumes
header_binance = "👉  BINANCE TRADES BTC  👈"
binance_volumes = display_format(binance)
message_binance = f"{header_binance}\n \n {binance_volumes}\n "













