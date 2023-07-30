# ---------------------------------------------------------
#                   IMPORT
# ---------------------------------------------------------


######################################
#### TELEGRAM WORKING PACKAGES  ###
######################################
import logging

from telegram import Update, error
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
# Ajoute cette ligne au début du fichier pour importer la classe `ReplyKeyboardMarkup`
from telegram import ReplyKeyboardMarkup


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
import oshi_plus as oshi

# ---------------------------------------------------------
#                   CONFIG
# ---------------------------------------------------------
config = dotenv_values(".env")
key = config['KEY']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


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



#           ---------------------------------------------------------
#                              BOT COMMANDS
#           ---------------------------------------------------------


# ---------------------------------------------------------
#                   CONVERSION
# ---------------------------------------------------------

async def btc2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = float(context.args[0]) if context.args else None
    if user_input is not None:
        res = "{:=,}".format(convert.btceur(user_input, 0))
        user_input = "{:=,}".format(user_input)
        message = f"{user_input} BTC = {res} EUR"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of bitcoin you want to convert in Euro! Enter /btc2eur your_amount.")


async def eur2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = float(context.args[0]) if context.args else None
    if user_input is not None:
        res = "{:=,}".format(convert.btceur(user_input, 1))
        user_input = "{:=,}".format(user_input)
        message = f"{user_input} EUR = {res} BTC"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of bitcoin you want to transform in Euro! Enter /eur2btc your_amount.")


async def btc2sats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_input = float(context.args[0]) if context.args else None
    sat = 10**8
    if btc_input is not None:
        sat_conversion = "{:=,}".format(convert.satsbtc(btc_input, 1))
        btc_input = "{:=,}".format(btc_input)
        message = f"{btc_input} BTC = {sat_conversion} sats"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of bitcoin you want to transform in sats! Enter /btc2sats your_btc_amount.")


async def sats2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    try:
        sats_input = int(context.args[0]) if context.args else None
        btc = 10**(-8)
        if sats_input is not None:
            btc_conversion = "{:=,}".format(convert.satsbtc(sats_input, 0))
            sats_input = "{:=,}".format(sats_input)

            message = f"{sats_input} sats = {btc_conversion} BTC"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The amount of satoshis (sats) is an INTEGER ! Enter /sats2btc your_sats_amount.")


async def sats2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    try:
        sats_input = int(context.args[0]) if context.args else None
        if sats_input is not None:
            res = "{:=,}".format(convert.satseur(sats_input, 0))
            sats_input = "{:=,}".format(sats_input)
            message = f"{sats_input} sats = {res} €"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of satoshis (sats) you want to transform in euros! The amount is an INTEGER ! Take care. Enter /sats2eur your_sats_amount.")


async def eur2sats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    eur_input = float(context.args[0]) if context.args else None
    if eur_input is not None:
        res = "{:=,}".format(convert.satseur(eur_input, 1))
        eur_input = "{:=,}".format(eur_input)
        message = f"{eur_input} € = {res} sats"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of euros you want to transform in sats! Enter /eur2sats your_eur_amount.")

# ---------------------------------------------------------
#                  DISPLAY CODE
# ---------------------------------------------------------


async def codeFetchPrices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('./fetch_prices.py', 'r') as f:
        lines = f.readlines()
    message = lines
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def codeConvert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('./convert.py', 'r') as f:
        lines = f.readlines()
    message = lines
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)



async def codeBot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('./bot.py', 'r') as f:
        lines = f.readlines()
    message = lines
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# ---------------------------------------------------------
#               VOLUME COMMANDS
# ---------------------------------------------------------

async def major_volumes(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
#               GENERAL COMMANDS
# ---------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rand = random.randint(0, 1)
    message_start = f"Welcome on SatoshiPriceBot 👋, \n Here you can find different information about bitcoin with /btcInfo command. You can also make conversions between btc and euro or btc and satoshis. \n To have the full commands list please try /help.\n For any suggestions you can contact @Dev_block. \n See you 🔜 in the /help message.\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_start)


async def btcPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_help = f"Here you can find details of all available commands 🖲️ : \n\n"
    sep2 = "\n --------  CONVERSION SATS <-> BTC <-> EUR  ------- \n \n"
    message_btc2eur = f"/btc2eur : Enter the command followed by the amount of btc you want to convert in eur. Ex : /btc2eur 0.1 \n"
    message_eur2btc = f"/eur2btc : Enter the command followed by the amount of euros you want to convert in btc. Ex : /eur2btc 10000 \n"
    message_btc2sats = f"/btc2sats : Enter the command followed by the amount of btc you want to convert in sats. Ex : /btc2sats 0.1 \n"
    message_sats2btc = f"/sats2btc : Enter the command followed by the amount of sats you want to convert in btc. Ex : /sats2btc \n"
    message_sats2eur = "/sats2eur : Enter the command followed by the amount of sats you want to convert in eur. Ex : /sats2eur 10000 \n "
    message_eur2sats = "/eur2sats : Enter the command followed by the amount of eur you want to convert in sats. Ex : /eur2sats 100 \n "

    sep3 = "\n ------  DISPLAY CODE USED  ---------- \n \n"
    message_codePrices = f"/codeFetchPrices : Give the code to fetch prices. It's mainly to develop for myself but you can check the code if you want 😉 \n"
    message_codeConvert = f"/codeConvert : Give the code to make every conversion used here. 💱\n "
    message_codeBot = f"/codeBot : Give my code. 🤖 Unfortunately, my code is too long to be displayed. Feel free to check my description to have more details.\n"

    sep_vol = "\n ------  VOLUMES DATA  ---------- \n \n"
    message_major_volumes = f"/majorVolumes : Provide information about most traded BTC pairs with the exchange 💹 \n"
    message_kraken_volumes = "/kraken : Provide information about BTC pairs traded on Kraken 🦈 \n "
    message_binance_volumes = "/binance : Provide information about BTC pairs traded in Binance 🅱️ \n"

    sep_general = "\n -----------  GENERAL/INFORMATIVE COMMANDS  ------------ \n \n"
    message_start = f"/start : A simple message to introduce the bot 🥳 \n"
    message_btcPrice = f"/btcPrice : Return the current price of btc in euro with a tiny message. Be cool 😎 \n"
    message_btcInfo = f"/btcInfo : Miscellaneous data about btc from binance. Stay informed 🤙 \n"
    message_btcATH = f"/btcATH : Give basic data about last All Time High (ATH) 📈 \n"
    message_btcMovements = f"/btcMovements : Give percentage variations on several time frames 🕰️ \n "
    message_btcSupply = f"/btcSupply : Give the actual Bitcoin supply and its value. 🤑 \n "
    message_btcPublicEngagement = f"/btcPublicEngagement : Measure of interest took from coingecko📱\n"
    message_btcDevEngagement = f"/btcDevEngagement: Some measure from github `bitcoin` repo 😼 \n "
    message_oshi = "/oshi : Fetch Last price of OSHI from unisat.\n " #TODO : Details OSHI project
    message_ordi = "/ordi : Fetch last price of ORDI from unisat. "#TODO : Tell the story about ORDI

    message_help += sep2 + message_btc2eur + message_eur2btc + message_btc2sats + message_sats2btc + message_sats2eur + message_eur2sats + sep3 + message_codePrices+message_codeConvert + \
        message_codeBot +sep_vol + message_major_volumes +message_kraken_volumes + message_binance_volumes + sep_general + message_start + message_btcPrice + message_btcInfo + message_btcATH + \
        message_btcMovements + message_btcSupply + message_btcPublicEngagement + message_btcDevEngagement + message_oshi + message_ordi
    message_help += "/help : Display this message 💬 \n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_help)

if __name__ == '__main__':
    application = ApplicationBuilder().token(key).build()

    eur2btc_handler = CommandHandler('eur2btc', eur2btc)
    btc2eur_handler = CommandHandler('btc2eur', btc2eur)
    btc2sats_handler = CommandHandler('btc2sats', btc2sats)
    sats2btc_handler = CommandHandler('sats2btc', sats2btc)
    sats2eur_handler = CommandHandler('sats2eur', sats2eur)
    eur2sats_handler = CommandHandler('eur2sats', eur2sats)

    codeConvert_handler = CommandHandler('codeConvert', codeConvert)
    codeBot_handler = CommandHandler('codeBot', codeBot)
    codePrices_handler = CommandHandler('codePrices', codeFetchPrices)

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

    oshi_handler = CommandHandler('oshi', oshi_)
    ordi_handler = CommandHandler('ordi', ordi) 
    help_handler = CommandHandler('help', helper)

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

    application.add_handler(eur2btc_handler)
    application.add_handler(btc2eur_handler)
    application.add_handler(btc2sats_handler)
    application.add_handler(sats2btc_handler)
    application.add_handler(sats2eur_handler)
    application.add_handler(eur2sats_handler)

    application.add_handler(codePrices_handler)
    application.add_handler(codeConvert_handler)
    application.add_handler(codeBot_handler)

    application.add_handler(majorVolumes_handler)
    application.add_handler(krakenVolumes_handler)
    application.add_handler(binanceVolumes_handler)


    application.run_polling()

