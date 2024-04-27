#@author: GaloisField
#@update: Add Runes selling infos from unisat.
#@minor: Add runes info
# ---------------------------------------------------------
#                   IMPORT
# ---------------------------------------------------------


######################################
#### TELEGRAM WORKING PACKAGES  ###
######################################
import logging

from telegram import Update, error
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
from telegram import ReplyKeyboardMarkup
from telegram import InputMediaPhoto #To reply with a Photo

#####################################
### PACKAGE FOR .env hidden file ####
###################################
from dotenv import dotenv_values

#################################
## PACKAGES TO CREATE ##########
### OPTIONS       ######
#############################
import random
from fetch_prices import CoinDataFetcher
import convert
from datetime import datetime, timedelta, timezone
import json
import oshi_plus as oshi
from fees import Fees
#@v6
import fetch_runes

import os

# ---------------------------------------------------------
#                   CONFIG
# ---------------------------------------------------------
config = dotenv_values(".env")
key = config['KEY']

# Define a custom filter class to exclude log records with specific messages
class ExcludeGetUpdatesFilter(logging.Filter):
    def filter(self, record):
        # Print the log message for debugging
        print(record.getMessage())
        return f"HTTP Request: POST https://api.telegram.org/bot{key}/getUpdates \"HTTP/1.1 200 OK\"" not in record.getMessage()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get the root logger
logger = logging.getLogger()

# Create an instance of the custom filter class
exclude_get_updates_filter = ExcludeGetUpdatesFilter()

# Add the custom filter to exclude getUpdates messages
logger.addFilter(exclude_get_updates_filter)

# ---------------------------------------------------------
#                   UTILS
# ---------------------------------------------------------


def convert_str(data):
    printable_str = str(data).replace("{", "").replace("}", "")
    return printable_str


def display_format(major_volumes):
    major_volumes_str = ""
    for index in range(len(major_volumes)):
        # We pick a volume in the dict {"exchange", "volume", "trust_score", "last_trade", "url", "pair"}
        # We have to structure this data
        if index != len(major_volumes)-1:

            major_volumes_str += f"- {convert_str(major_volumes[index])} ; \n "
        else:
            major_volumes_str += f"- {convert_str(major_volumes[index])}.\n"

    return major_volumes_str


#---------------------------------------------------------
#---------------------------------------------------------
#                   BOT COMMANDS
#---------------------------------------------------------
#---------------------------------------------------------

# ---------------------------------------------------------
#                   CONVERSION
# ---------------------------------------------------------



async def btc2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("btc2eur called \n")        
    try :
        user_input = float(context.args[0]) if context.args else None
        if user_input is not None:
            res = "{:=,}".format(convert.btceur(user_input, 0))
            user_input = "{:=,}".format(user_input)
            message = f"{user_input} BTC = {res} EUR"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of bitcoin you want to convert in Euro! Enter /btc2eur your_amount.")
    # Handle case where a user enter 3,1 instead of 3.1
    except ValueError:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            user_input.replace(',', '.')
            amount_input = float(user_input)
            res = "{:=,}".format(convert.btceur(user_input, 0))
            user_input = "{:=,}".format(user_input)
            message = f"{user_input} BTC = {res} EUR"
            reminder = f"\n I remind you that in English format comma ',' are used to separate 3 numbers. To write 3,1 we write 3.1 ! Now it's fix, but take care for reading."
            message += reminder
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


    except Exception != ValueError as e: 
        logging.error(f"Error during conversion btc2eur: {e} in {update}\n")
        message_error = f"Error during conversion {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


async def eur2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("eur2btc called \n")
    try : 
        user_input = float(context.args[0]) if context.args else None
        if user_input is not None:
            res = "{:=,}".format(convert.btceur(user_input, 1))
            user_input = "{:=,}".format(user_input)
            message = f"{user_input} EUR = {res} BTC"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of bitcoin you want to transform in Euro! Enter /eur2btc your_amount.")

    except Exception as e: 
        logging.error(f"Error during conversion eur2btc: {e} in {update}\n")
        message_error = f"Error during conversion {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


async def btc2sat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        btc_input = float(context.args[0]) if context.args else None
        sat = 10**8
        if btc_input is not None:
            sat_conversion = "{:=,}".format(convert.satsbtc(btc_input, 1))
            btc_input = "{:=,}".format(btc_input)
            message = f"{btc_input} BTC = {sat_conversion} sats"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of bitcoin you want to transform in sat! Enter /btc2sat your_btc_amount.")
    except Exception as e:
        logging.error(f"Error during conversion btc2sat: {e} in {update}\n")
        message_error = f"Error during conversion {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)

async def sat2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("sat2btc called \n")
    try:
    # Manage float user entry instead of int
        sats_input = int(context.args[0]) if context.args else None
        btc = 10**(-8)
        if sats_input is not None:
            btc_conversion = "{:=,}".format(convert.satsbtc(sats_input, 0))
            sats_input = "{:=,}".format(sats_input)

            message = f"{sats_input} sats = {btc_conversion} BTC"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    except ValueError:
        logging.info("ValueError raised sat2btc in {update}\n")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The amount of satoshis (sat) is an INTEGER ! Enter /sat2btc your_sat_amount.")


async def sat2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("sat2eur called \n")
    try:
    # Manage float user entry instead of int
        sats_input = int(context.args[0]) if context.args else None
        if sats_input is not None:
            res = "{:=,}".format(convert.satseur(sats_input, 0))
            sats_input = "{:=,}".format(sats_input)
            message = f"{sats_input} sats = {res} €"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    except ValueError:
        logging.info("ValueError raised sat2eur in {update}\n")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of satoshis (sats) you want to transform in euros! The amount is an INTEGER ! Take care. Enter /sat2eur your_sats_amount.")


async def eur2sat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("eur2sat called \n")
    try : 
	    eur_input = float(context.args[0]) if context.args else None
	    if eur_input is not None:
	        res = "{:=,}".format(convert.satseur(eur_input, 1))
	        eur_input = "{:=,}".format(eur_input)
	        message = f"{eur_input} € = {res} sats"
	        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
	    else:
	        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of euros you want to transform in sats! Enter /eur2sats your_eur_amount.")

    except Exception as e:
        logging.error(f"Error during conversion eur2sat: {e} in {update}\n")
        message_error = f"Error during conversion {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)



# ---------------------------------------------------------
#                       FEES
# ---------------------------------------------------------


async def fees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("fees called \n")
    try : 
        fees = Fees()
        message = f"Mempool fees 🚀 : \n No priority : {fees.no_priority}, Low priority : {fees.low_fees}, Mid priority : {fees.medium_fees}, High priority : {fees.max_fees} "
        await context.bot.send_message(chat_id= update.effective_chat.id, text=message)

    except Exception as e:
        logging.error(f"An unexpected error occurred in fees: {e} with {update}\n")
        error_message = f"A fetch error happened : {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)


# This is to catch max fees in an easy copying format
async def max_fees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("maw_fees called \n")
    try : 
        fees = Fees()
        max_fees = fees.get_max_fees()
        message = f"{max_fees}"
        await context.bot.send_message(chat_id= update.effective_chat.id, text=message)

    except Exception as e:
        logging.error(f"An unexpected error occurred in max_fees: {e} with {update}")
        error_message = f"A fetch error happened : {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)



# ---------------------------------------------------------
#               VOLUME COMMANDS
# ---------------------------------------------------------

async def major_volumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("major_volumes called\n")
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    tickers = fetcher.get_tickers(data)
    all_volumes = fetcher.get_all_volumes(tickers)
    major_volumes = fetcher.get_major_volumes(all_volumes)
    
    # Major volumes
    header_major_volumes = "👉  5 MOST TRADED PAIRS WITH EXCHANGE  👈 "
    major_volumes_str = display_format(major_volumes)
    message_major_volumes = f"{header_major_volumes}\n\n {major_volumes_str} \n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_major_volumes)


async def binance_volumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("binance_volumes called \n")
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    tickers = fetcher.get_tickers(data)
    all_volumes = fetcher.get_all_volumes(tickers)
    
    binance = fetcher.get_binance_volumes(all_volumes)

    # Binance volumes
    header_binance = "👉  BINANCE TRADES BTC  👈"
    binance_volumes = display_format(binance)
    message_binance = f"{header_binance}\n \n {binance_volumes}\n "

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_binance)


async def kraken_volumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("kraken_volumes called \n")
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    tickers = fetcher.get_tickers(data)
    all_volumes = fetcher.get_all_volumes(tickers)

    kraken = fetcher.get_kraken_volumes(all_volumes)

    # Kraken volumes
    header_kraken = "👉  KRAKEN TRADES BTC  👈"
    kraken_volumes = display_format(kraken)
    message_kraken = f"{header_kraken} \n \n {kraken_volumes}\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_kraken)

# ---------------------------------------------------------
#               RUNES COMMANDS
# ---------------------------------------------------------

async def runeinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nb_args = len(context.args)
    logging.info(f"runeinfo called with {nb_args} arguments\n")
    if nb_args == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a Rune name to get info. You need to use '.' or '•'. No white space. You can enter a list of Runes with space between Rune.\n")
    elif nb_args == 1:
        rune = context.args[0]
        message = fetch_runes.info_message(rune)        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        for index in range(nb_args):
            rune = context.args[index]
            message = fetch_runes.info_message(rune) 
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        await context.bot.send_message(chat_id:=update.effective_chat.id, text="👍 Done! 🚀")

async def runefloor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nb_args = len(context.args)
    logging.info(f"runefloor called with {nb_args} arguments \n")
    if nb_args == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter at least one Rune name (whitout space). You can enter list with spacing each names.")
    else:
        for index in range(nb_args):
            rune = context.args[index]
            rune_name = fetch_runes.parse_rune_name(rune)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔍 I will ask to unisat to get the lastest floor about {rune_name}. Please wait a second...")
            message = fetch_runes.floor_listing(rune)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            await context.bot.send_message(chat_id=update.effective_chat.id, text = f"For all listing: https://unisat.io/runes/market?tick={rune_name.replace('•','%E2%80%A2')}")

async def runemc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nb_args = len(context.args)
    logging.info(f"runemc was called with {nb_args} arguments: {update}\n")
    if nb_args == 0:
         await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter at least one Rune name (whitout space). You can enter list with spacing each names.")
    elif nb_args == 1:
        rune = context.args[0]
        rune_name = fetch_runes.parse_rune_name(rune)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔍 I will ask to unisat to get last floor about {rune_name}. Please wait a second...")
        (btc_marketcap, usd_marketcap) = fetch_runes.get_marketcap(rune)
        message = f"{rune_name}\n"
        message += f"${'{:,}'.format(usd_marketcap)} = {btc_marketcap}BTC"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text = f"For all listing: https://unisat.io/runes/market?tick={rune_name.replace('•','%E2%80%A2')}")

    else:
        runes = [context.args[index] for index in range(nb_args)]
        runes_name = [fetch_runes.parse_rune_name(rune) for rune in runes]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔍 I will ask to unisat to get last floor about {runes_name}. Please wait a second...")
        for rune_name in runes_name:
            try:
                (btc_marketcap, usd_marketcap) = fetch_runes.get_marketcap(rune_name)
            except:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error happening. Couldn't get marketcap from unisat. Look about the existence of your rune. Maybe it's because there is no listing.")

            message = f"\t \t 👉{rune_name}👈\n"
            message += f"👉 ${'{:,}'.format(usd_marketcap)} = {btc_marketcap}BTC"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message) 
            await context.bot.send_message(chat_id=update.effective_chat.id, text = f"For all listing: https://unisat.io/runes/market?tick={rune_name.replace('•','%E2%80%A2')}")

        await context.bot.send_message(chat_id=update.effective_chat.id, text="👍 Done!🚀")
        
# ---------------------------------------------------------
#               GENERAL COMMANDS
# ---------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rand = random.randint(0, 1)
    message_start = f"Welcome on SatoshiPriceBot 👋, \n Here you can find different information about bitcoin with /btcInfo command. You can also make conversions between btc and euro or btc and satoshis. \n To have the full commands list please try /help.\n For any suggestions you can contact @Dev_block. \n See you 🔜 in the /help message.\n \n 👉 If you want to help the hosting 🎛️ of the bot you can send some sats at 💶bc1qxxuuxmlp3wxuyn6uuqw448nzaafuqdxc076m9k 👈."
    logging.info(f"Call `start` from {update.message.chat}.\n Update: {update}\n")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_start)


async def btcPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("btcPrice called")
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)

    price = fetcher.get_current_price(market_data)
    price_str = f"{price:,.0f}"
    # Time management
    date_str = fetcher.get_timestamp(market_data)
    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    # Convertir la date en fuseau horaire UTC+2
    date = date.astimezone(timezone(timedelta(hours=2)))
    message_price = f"At {date} (Paris timezone) : 1 BTC = {price_str} EUR. \n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_price)


async def btcInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)
    description = fetcher.get_description(data)
    genesis = fetcher.get_genesis_date(data)
    ath_data = fetcher.get_ath_data(market_data)
    supply = fetcher.get_circulating_supply(market_data)
    actual_supply_str = f"{supply:,.0f}"
    ath = ath_data['ath']
    change_from_ath = ath_data['ath_change']
    ath_str = f"{ath:,.0f}"
    ath_date = ath_data['ath_date']
    fdv = fetcher.get_fdv(market_data)
    fully_diluted_valuation = f"{fdv:,.0f}"

    message_ath = f"Bitcoin All Time High (ATH) was {ath_str} EUR at {ath_date}. Since ATH, Bitcoin dropped by : {change_from_ath}%.\n"
    message_supply = f"Actual supply of Bitcoin is {actual_supply_str} BTC, for a fully diluted market cap : {fully_diluted_valuation} EUR. \n "
    message_info = f"Bitcoin was born {genesis}, it can be described as like this :\n {description}\n {message_ath}\n {message_supply}\n For more information take a look on informative commands.\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_info)


async def btcATH(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)
    ath_data = fetcher.get_ath_data(market_data)
    ath = ath_data['ath']
    ath_str = f"{ath:,.0f}"
    ath_date = ath_data['ath_date']
    change_from_ath = ath_data['ath_change']

    message_ath = f"Bitcoin All Time High (ATH) was {ath_str} EUR at {ath_date}. Since ATH, Bitcoin dropped by : {change_from_ath}%.\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_ath)


async def btcMovements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)
    percent_changes = fetcher.get_percentage_changes(market_data)

    message_change = f"Bitcoin movements against Euro 💶 : \n - In 1 hour Bitcoin moves : {percent_changes['1h']}% ;\n - In 24 hours : {percent_changes['24h']}% ;\n - In 7 days : {percent_changes['7d']}% ; \n - In 30 days : {percent_changes['30d']}% ;\n - In 200 days : {percent_changes['200d']}% ;\n - In 1 year : {percent_changes['1y']}%.\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_change)


async def btcSupply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    market_data = fetcher.get_market_data(data)
    supply = fetcher.get_circulating_supply(market_data)
    actual_supply_str = f"{supply:,.0f}"
    fdv = fetcher.get_fdv(market_data)
    fully_diluted_valuation = f"{fdv:,.0f}"

    message_supply = f"Actual supply of Bitcoin is {actual_supply_str} BTC, for a fully diluted market cap : {fully_diluted_valuation} EUR. \n "
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_supply)


async def btcPublicEngagement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    public = fetcher.get_public(data)

    message_public = f"A simple measure of interest took from coingecko : {public}.\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_public)

async def oshi_(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please wait it's loading ....") 
    (price_sats, amount_oshi, price_usd, price_btc) = oshi.fetch("oshi")
    price_sats = "{:=,}".format(price_sats)
    message = f"Price per OSHI : {price_sats} sats. \n\n"
    message += f'Pack : {amount_oshi} OSHI for {price_usd} = {price_btc} BTC'
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message) 

async def ordi(update: Update, context: ContextTypes.DEFAULT_TYPE) :
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please wait it's loading ....") 
    (price_sats, amount_ordi, price_usd, price_btc) = oshi.fetch("ordi")
    price_sats = "{:=,}".format(price_sats)
    message = f"Price per ORDI: {price_sats} sats. \n\n"
    message += f'Pack : {amount_ordi} ORDI for {price_usd} = {price_btc} BTC'
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message) 

async def getlastprice(update: Update, context: ContextTypes.DEFAULT_TYPE): #TODO: Error management if name isn't catched or other issues with chrome browser
    logging.info("getlastprice called for {context.args[0]}\n")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please wait it's loading ....")
    token = context.args[0] if context.args else None
    if token is not None:
        (price_sats, amount_token, price_usd, price_btc) = oshi.fetch(token.lower())
        price_sats = "{:=,}".format(price_sats)
        message = f"Price per {token.upper()}: {price_sats} sats. \n\n"
        message += f'Pack : {amount_token} {token.upper()} for {price_usd} = {price_btc} BTC'

        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the name of brc-20 you're looking for ! Ex : Ordi, oshi, YARI,...")

async def btcDevEngagement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DATA
    fetcher = CoinDataFetcher('bitcoin')
    data = fetcher.get_coin_data()
    dev_data = fetcher.get_dev_data(data)
    forks = dev_data["forks"]
    stars = dev_data["stars"]
    subs = dev_data["subscribers"]
    total_issues = dev_data["total_issues"]
    pull_requests = dev_data["pull_requests_merged"]
    contributors = dev_data["pull_request_contributors"]
    # { "additions": 4932,"deletions": -1770}
    additions_deletions = dev_data["code_additions_deletions_4_weeks"]
    commit_4w = dev_data["commit_count_4_weeks"]

    message_dev = f"From Github repo (https://github.com/bitcoin/bitcoin) we have : \n - {forks} forks ; \n  - {stars} stars ; \n - {subs} subscribers ; \n - {total_issues} total issues reported ; \n {pull_requests} pull requests to merge ; \n - {contributors} contributors ; \n - {additions_deletions['additions']} additions for {additions_deletions['deletions']} deletions ; \n - {commit_4w} commits on last 4 weeks.\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_dev)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"support called by {update.message.chat.username}\n")
    message = "You want to support the hosting of the bot ⁉️ You can send some sats at 👉bc1qxxuuxmlp3wxuyn6uuqw448nzaafuqdxc076m9k👈.\n I'm hosted at Hostinger and payment can be done in Bitcoin ! So, your money will directly go to Hostinger 🙃. "
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    pic = os.path.join(os.getcwd(), 'qr_generator', 'qr_myaddress.png')
    print(os.getcwd())

    await context.bot.send_photo(chat_id=update.effective_chat.id,photo=pic)



async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_help = "Here you can find details of all available commands 🖲️ : \n\n"
    message_update = "\n  📣 NEW UPDATE --> RUNES INFO FROM UNISAT! See RUNES section\n \n "    
    sep2 = "\n --- 🔄  CONVERSION SATS <-> BTC <-> EUR  --- \n \n"
    
    remind_numbers = "\n I WANT TO REMIND THAT DECIMALS NUMBERS IN ENGLISH ARE WRITTEN WITH A DOT : 100.87 ! I STILL DON'T MANAGE NUMBERS WITH : 100,87 \n"
    message_btc2eur = f"/btc2eur : Enter the command followed by the amount of btc you want to convert in eur. Ex : /btc2eur 0.1 \n"
    message_eur2btc = f"/eur2btc : Enter the command followed by the amount of euros you want to convert in btc. Ex : /eur2btc 10000 \n"
    message_btc2sat = f"/btc2sat : Enter the command followed by the amount of btc you want to convert in sats. Ex : /btc2sat 0.1 \n"
    message_sat2btc = f"/sat2btc : Enter the command followed by the amount of sats you want to convert in btc. Ex : /sat2btc \n"
    message_sat2eur = "/sat2eur : Enter the command followed by the amount of sats you want to convert in eur. Ex : /sat2eur 10000 \n "
    message_eur2sat = "/eur2sat : Enter the command followed by the amount of eur you want to convert in sats. Ex : /eur2sat 100 \n "

    sep_fees = "\n ---- FEES ON THE MEMPOOL  ------\n\n"
    message_fees = f"/fees : Get general fees information from mempool.space. Standalone command 🖲️\n "
    message_max_fees = f"/maxfees : Get only max fees from Mempool. Useful to copy paste the max fees.\n"
    
    sep_brc20 = f"\n ------ BRC-20 DATA  -------  \n \n "
    message_oshi = "/oshi : Fetch Last price of OSHI from unisat.\n " #TODO : Details OSHI project
    message_ordi = "/ordi : Fetch last price of ORDI from unisat. \n "#TODO : Tell the story about ORDI
    message_getlastprice = "/getlastprice `token` : Fetch the last price from Unisat of `token`. Ex : /getlastprice yari (not case sensitive for token). \n "
    message_support = "/support : 🤗😇🥰.\n\n"
    
    sep_general = "\n ------  GENERAL/INFORMATIVE COMMANDS  ------ \n \n"
    message_start = f"/start : A simple message to introduce the bot 🥳 \n"
    message_btcPrice = f"/btcPrice : Return the current price of btc in euro with a tiny message. Be cool 😎 \n"
    message_btcInfo = f"/btcInfo : Miscellaneous data about btc from binance. Stay informed 🤙 \n"
    message_btcATH = f"/btcATH : Give basic data about last All Time High (ATH) 📈 \n"
    message_btcMovements = f"/btcMovements : Give percentage variations on several time frames 🕰️ \n "
    message_btcSupply = f"/btcSupply : Give the actual Bitcoin supply and its value. 🤑 \n "
    message_btcPublicEngagement = f"/btcPublicEngagement : Measure of interest took from coingecko📱\n"
    message_btcDevEngagement = f"/btcDevEngagement: Some measure from github `bitcoin` repo 😼 \n "

    sep_vol = "\n ----  VOLUMES DATA  ------- \n \n"
    message_major_volumes = f"/majorVolumes : Provide information about most traded BTC pairs with the exchange 💹 \n"
    message_kraken_volumes = "/kraken : Provide information about BTC pairs traded on Kraken 🦈 \n "
    message_binance_volumes = "/binance : Provide information about BTC pairs traded in Binance 🅱️ \n"

    sep_rune = "\n ----  RUNES INFORMATION  ------- \n \n" 
    message_runeinfo = "/runeinfo: Provide all basics information about one or many runes. USAGE: /runeinfo satoshi.nakamoto rsic.genesis.rune\n"
    message_runefloor = "/runefloor: Provide details about floor price listing on Unisat. You can find the marketcap assiociated with this price ($ and BTC). USAGE:\n 1. /runefloor your.rune.name\n 2. /runefloor first.rune second.rune. \n Note: You can •, . or unicode. [Needs improvments on error handling] \n"
    message_runemc = "/runemc: Provide rune name and marketcap only. Shorter than /runefloor! USAGE:\n 1. /runemc your.rune.name\n 2. /runemc your_rune.1 your.rune.2 ...\n\n"

    message_help += message_update + sep2 + remind_numbers + message_btc2eur + message_eur2btc + message_btc2sat + message_sat2btc + message_sat2eur + message_eur2sat + sep_fees + message_fees + message_max_fees + \
    sep_brc20 + message_oshi + message_ordi + message_getlastprice + message_support + \
    sep_vol + message_major_volumes + message_kraken_volumes + message_binance_volumes + message_btcMovements + message_btcSupply + message_btcPublicEngagement + message_btcDevEngagement + \
    sep_general + message_start + message_btcPrice + message_btcInfo + message_btcATH + message_support + \
    sep_rune + message_runeinfo + message_runefloor + message_runemc 

    message_help += "/help : Display this message 💬 \n"
    logging.info(f"help called {update}\n")

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_help)

if __name__ == '__main__':
    application = ApplicationBuilder().token(key).build()

    eur2btc_handler = CommandHandler('eur2btc', eur2btc)
    btc2eur_handler = CommandHandler('btc2eur', btc2eur)
    btc2sat_handler = CommandHandler('btc2sat', btc2sat)
    sat2btc_handler = CommandHandler('sat2btc', sat2btc)
    sat2eur_handler = CommandHandler('sat2eur', sat2eur)
    eur2sat_handler = CommandHandler('eur2sat', eur2sat)

    fees_handler = CommandHandler('fees', fees)
    max_fees_handler = CommandHandler('maxfees', max_fees)

    majorVolumes_handler = CommandHandler('majorVolumes', major_volumes)
    krakenVolumes_handler = CommandHandler('kraken', kraken_volumes)
    binanceVolumes_handler = CommandHandler('binance', binance_volumes)

    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('btcPrice', btcPrice)
    info_handler = CommandHandler('btcInfo', btcInfo)
    btcATH_handler = CommandHandler('btcATH', btcATH)
    btcMovements_handler = CommandHandler('btcMovements', btcMovements)
    btcSupply_handler = CommandHandler('btcSupply', btcSupply)
    btcPublicEngagement_handler = CommandHandler(
        'btcPublicEngagement', btcPublicEngagement)
    btcDevEngagement_handler = CommandHandler(
        'btcDevEngagement', btcDevEngagement)
    
    runeinfo_handler = CommandHandler('runeinfo', runeinfo)
    runefloor_handler = CommandHandler('runefloor', runefloor)
    runemc_handler = CommandHandler('runemc', runemc)

    oshi_handler = CommandHandler('oshi', oshi_)
    ordi_handler = CommandHandler('ordi', ordi)
    getlastprice_handler = CommandHandler('getlastprice', getlastprice)
    help_handler = CommandHandler('help', helper)
    support_handler = CommandHandler('support', support)
    
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(price_handler)
    application.add_handler(info_handler)
    application.add_handler(btcATH_handler)
    application.add_handler(btcMovements_handler)
    application.add_handler(btcSupply_handler)
    application.add_handler(btcPublicEngagement_handler)
    application.add_handler(btcDevEngagement_handler)
    application.add_handler(oshi_handler)
    application.add_handler(ordi_handler)
    application.add_handler(getlastprice_handler)
    application.add_handler(support_handler)
    
    application.add_handler(runeinfo_handler)
    application.add_handler(runefloor_handler)
    application.add_handler(runemc_handler)

    application.add_handler(eur2btc_handler)
    application.add_handler(btc2eur_handler)
    application.add_handler(btc2sat_handler)
    application.add_handler(sat2btc_handler)
    application.add_handler(sat2eur_handler)
    application.add_handler(eur2sat_handler)

    application.add_handler(fees_handler)
    application.add_handler(max_fees_handler)

    application.add_handler(majorVolumes_handler)
    application.add_handler(krakenVolumes_handler)
    application.add_handler(binanceVolumes_handler)


    application.run_polling()

