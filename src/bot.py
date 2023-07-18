######################################
####	TELEGRAM WORKING PACKAGES  ###
######################################
import logging

from telegram import Update, error
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
# Ajoute cette ligne au début du fichier pour importer la classe `ReplyKeyboardMarkup`
from telegram import ReplyKeyboardMarkup


#####################################
###PACKAGE FOR .env hidden file ####
###################################
from dotenv import dotenv_values

#################################
##PACKAGES TO CREATE ##########
###	 OPTIONS       ######  		
#############################
import random
from fetch_prices import *
from messages import *
import convert


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
#                   CONVERSION                              
# ---------------------------------------------------------

async def btc2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
      user_input = float(context.args[0]) if context.args else None
      if user_input is not None: 
            res = "{:=,}".format(convert.btceur(user_input,0))
            user_input = "{:=,}".format(user_input)
            message = f"{user_input} BTC = {res} EUR"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

      else:
          await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of bitcoin you want to convert in Euro! Enter /btc2eur your_amount.")
		

async def eur2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = float(context.args[0]) if context.args else None
    if user_input is not None:
        res = "{:=,}".format(convert.btceur(user_input,1))
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
    sats_input = int(context.args[0]) if context.args else None
    btc = 10**(-8)
    if sats_input is not None:
        btc_conversion = "{:=,}".format(convert.satsbtc(sats_input,0))
        sats_input = "{:=,}".format(sats_input)

        message = f"{sats_input} sats = {btc_conversion} BTC" 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of satoshis you want to transform in btc! Enter /sats2btc your_sats_amount.")

async def sats2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    sats_input = int(context.args[0]) if context.args else None
    if sats_input is not None:
        res = "{:=,}".format(convert.satseur(sats_input, 0))
        sats_input = "{:=,}".format(sats_input)
        message = f"{sats_input} sats = {res} €" 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of satoshis you want to transform in euros! Enter /sats2eur your_sats_amount.")


async def eur2sats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    eur_input = float(context.args[0]) if context.args else None
    if eur_input is not None:
        res = "{:=,}".format(.convert.satseur(eur_input, 1))
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
async def codeMessages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('./messages.py', 'r') as f:
        lines = f.readlines()
    message = lines
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
async def codeBot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('./bot.py', 'r') as f:
        lines = f.readlines()
    message = lines
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)




# ---------------------------------------------------------
#               GENERAL COMMANDS
# ---------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	rand = random.randint(0,1)
	message_start = f"Welcome on SatoshiPriceBot 👋, \n Here you can find different information about bitcoin with /btcInfo command. You can also make conversions between btc and euro or btc and satoshis. \n To have the full commands list please try /help.\n For any suggestions you can contact @Dev_block. \n See you 🔜 in the /help message.\n"
	await context.bot.send_message(chat_id=update.effective_chat.id, text=message_start)

async def btcPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id = update.effective_chat.id, text=message_price)

async def btcInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id = update.effective_chat.id, text=message_info)

async def btcATH(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_ath)

async def btcMovements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id= update.effective_chat.id, text=message_change)


async def btcSupply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id= update.effective_chat.id, text=message_supply)

async def btcPublicEngagement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id= update.effective_chat.id, text=message_public)

async def btcDevEngagement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id= update.effective_chat.id, text=message_dev)




	
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
    message_codeMessages = f"/codeMessages : Give the code where technical messages are written. 📗\n "
    message_codeBot = f"/codeBot : Give my code. 🤖 Unfortunately, my code is too long to be displayed. Feel free to check my description to have more details.\n"

    sep_general = "\n -----------  GENERAL COMMANDS  ------------ \n \n"
    message_start = f"/start : A simple message to introduce the bot 🥳 \n"
    message_btcPrice = f"/btcPrice : Return the current price of btc in euro with a tiny message. Be cool 😎 \n"
    message_btcInfo = f"/btcInfo : Miscellaneous data about btc from binance. Stay informed 🤙 \n"
    message_btcATH = f"/btcATH : Give basic data about last All Time High (ATH) 📈 \n"
    message_btcMovements = f"/btcMovements : Give percentage variations on several time frames 🕰️ \n "
    message_btcSupply = f"/btcSupply : Give the actual Bitcoin supply and its value. 🤑 \n "
    message_btcPublicEngagement = f"/btcPublicEngagement : Measure of interest took from coingecko📱\n"
    message_btcDevEngagement = f"/btcDevEngagement: Some measure from github `bitcoin` repo 😼 \n "


    message_help += sep2 + message_btc2eur + message_eur2btc + message_btc2sats + message_sats2btc + message_sats2eur + message_eur2sats + sep3 +  message_codePrices+message_codeConvert + message_codeMessages + message_codeBot +sep_general + message_start + message_btcPrice + message_btcInfo + message_btcATH + message_btcMovements + message_btcSupply + message_btcPublicEngagement + message_btcDevEngagement
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
    codeMessages_handler = CommandHandler('codeMessages', codeMessages)
    codeBot_handler = CommandHandler('codeBot', codeBot)
    codePrices_handler = CommandHandler('codePrices',codeFetchPrices)
    
    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('btcPrice', btcPrice)
    info_handler = CommandHandler('btcInfo', btcInfo)
    btcATH_handler = CommandHandler('btcATH',btcATH)
    btcMovements_handler = CommandHandler('btcMovements', btcMovements)
    btcSupply_handler = CommandHandler('btcSupply', btcSupply) 
    btcPublicEngagement_handler = CommandHandler('btcPublicEngagement', btcPublicEngagement)
    btcDevEngagement_handler = CommandHandler('btcDevEngagement', btcDevEngagement)



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

    application.add_handler(eur2btc_handler)
    application.add_handler(btc2eur_handler)
    application.add_handler(btc2sats_handler)
    application.add_handler(sats2btc_handler)
    application.add_handler(sats2eur_handler)
    application.add_handler(eur2sats_handler)
    
    application.add_handler(codeMessages_handler)
    application.add_handler(codePrices_handler)
    application.add_handler(codeConvert_handler)
    application.add_handler(codeBot_handler)
    
    application.run_polling()

