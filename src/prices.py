# Import pour récupérer les datas
import pandas as pd
from binance.client import Client
from datetime import datetime

# To shutdown pandas warnings
import warnings
warnings.filterwarnings('ignore') # setting ignore as a parameter


# Define Client() as client
client = Client()

# Name of coin
coin = 'BTC'
fiat = 'EUR'
# Arguments for ticker
p = coin+fiat
ticker = client.get_ticker(symbol=p)


price = round(float(ticker['lastPrice']),3)
#print(price)

#############################################################
#######		IMPORTANT VARIABLES		##############
#############################################################
price = round(float(ticker['lastPrice']),3)
variations = round(float(ticker['priceChangePercent']),2) 
volumeToken = round(float(ticker['volume']),3) 
volumeEUR = round(float(ticker['quoteVolume']),3) 



currentDateAndTime = datetime.now()
currentTime = currentDateAndTime.strftime("Le %D, à %H:%M:%S")


 ###############################################################
######		MESSAGES 		#######################
###############################################################
text_price = "{:=,}".format(price)
text_volumeEUR = "{:=,}".format(volumeEUR)
text_volumeToken = "{:=,}".format(volumeToken)

message_info= f"{currentTime} : Le BTC est à {text_price}€, avec un volume de {text_volumeEUR}€ et {text_volumeToken}BTC, avec une variation de {variations}% en 24 heures."

message_cours = f"{currentTime} : Le BTC est à {text_price}€."


