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
import prices


config = dotenv_values(".env")
key = config['KEY']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	rand = random.randint(0,1)
	message_start = f"Welcome on SatoshiPriceBot 👋, \n Here you can find different information about bitcoin with /btcInfo command. You can also make conversions between btc and euro or btc and satoshis. \n To have the full commands list please try /help.\n For any suggestions you can contact @Dev_block. \n See you soon on the /help message 🔜.\n"
	await context.bot.send_message(chat_id=update.effective_chat.id, text=message_start)


async def btc2eur(update: Update,context : ContextTypes.DEFAULT_TYPE):
	user_input = float(context.args[0]) if context.args else None
	if user_input is not None:
		result = round(user_input*prices.price, 2)
		message = f"{user_input} BTC = {result} EUR"
		await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
	else:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of bitcoin you want to convert in Euro! Enter /btc2eur your_amount.")


async def eur2btc(update: Update,context : ContextTypes.DEFAULT_TYPE):
	user_input = float(context.args[0]) if context.args else None
	if user_input is not None:
		result = round(user_input/prices.price,8)
		message = f"{user_input} EUR = {result} BTC"
		await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
	else:
		await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of bitcoin you want to transform in Euro! Enter /eur2btc your_amount.")

async def btc2sats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_input = float(context.args[0]) if context.args else None
    sat = 10**8
    if btc_input is not None:
        sat_conversion = round(btc_input * sat, 8)
        sat_conversion = "{:=,}".format(sat_conversion)
        message = f"{btc_input} BTC = {sat_conversion} sats"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of bitcoin you want to transform in sats! Enter /btc2sats your_btc_amount.")

async def sats2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    sats_input = int(context.args[0]) if context.args else None
    btc = 10**(-8)
    if sats_input is not None:
        btc_conversion = round(sats_input * btc, 8)
        btc_conversion = "{:=,}".format(btc_conversion)
        sats_input = "{:=,}".format(sats_input)

        message = f"{sats_input} sats = {btc_conversion} BTC" 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of satoshis you want to transform in btc! Enter /sats2btc your_sats_amount.")

async def sats2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    sats_input = int(context.args[0]) if context.args else None
    if sats_input is not None:
        btc = sats_input*10**(-8)
        eur = prices.price
        res = round(eur*btc, 3)
        res = "{:=,}".format(res)
        message = f"{sats_input} sats = {res} €" 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the number of satoshis you want to transform in euros! Enter /sats2eur your_sats_amount.")


async def eur2sats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Gérer le fait que l'utilisateur mette un décimal qui est une erreur
    eur_input = float(context.args[0]) if context.args else None
    if eur_input is not None:
        sats = 10**8
        eur = prices.price
        res = int((sats*eur_input)/eur)
        res = "{:=,}".format(res)
        message = f"{eur_input} € = {res} sats" 
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the amount of euros you want to transform in sats! Enter /eur2sats your_eur_amount.")



async def codePrices(update: Update, context: ContextTypes.DEFAULT_TYPE):
	with open('./prices.py', 'r') as f:
		lines = f.readlines()
	message = lines 
	await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def btcPrice(update: Update, context: ContextTypes.DEFAULT_TYPE):
	message_price = prices.message_cours
	print(message_price)
	await context.bot.send_message(chat_id = update.effective_chat.id, text=message_price)

async def btcInfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	message_info = prices.message_info
	print(message_info)
	await context.bot.send_message(chat_id = update.effective_chat.id, text=message_info)

	
async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_help = f"Here you can find details of available commands 🖲️ : \n"
    message_start = f"/start : A simple message to introduce the bot 🥳 \n"
    message_btc2eur = f"/btc2eur : Enter the command followed by the amount of btc you want to convert in eur. Ex : /btc2eur 0.1 \n"
    message_eur2btc = f"/eur2btc : Enter the command followed by the amount of euros you want to convert in btc. Ex : /eur2btc 10000 \n"
    message_btc2sats = f"/btc2sats : Enter the command followed by the amount of btc you want to convert in sats. Ex : /btc2sats 0.1 \n"
    message_sats2btc = f"/sats2btc : Enter the command followed by the amount of sats you want to convert in btc. Ex : /sats2btc \n"
    message_sats2eur = "/sats2eur : Enter the command followed by the amount of sats you want to convert in eur. Ex : /sats2eur 10000 \n "
    message_eur2sats = "/eur2sats : Enter the command followed by the amount of eur you want to convert in sats. Ex : /eur2sats 100 \n "
    message_codePrices = f"/codePrices : Give the code to peak prices. It's mainly to develop for myself but you can check the code if you want 😉 \n"
    message_btcPrice = f"/btcPrice : Return the current price of btc in euro with a tiny message. Be cool 😎 \n"
    message_btcInfo = f"/btcInfo : Miscellaneous data about btc from binance. Stay informed 🤙 \n"

    message_help += message_start + message_btc2eur + message_eur2btc + message_btc2sats + message_sats2btc + message_sats2eur + message_eur2sats + message_codePrices + message_btcPrice + message_btcInfo
    message_help += "/help : Display this message 💬 \n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_help)

if __name__ == '__main__':
    application = ApplicationBuilder().token(key).build()
    
    start_handler = CommandHandler('start', start)
    price_handler = CommandHandler('btcPrice', btcPrice)
    info_handler = CommandHandler('btcInfo', btcInfo)
    codePrices_handler = CommandHandler('codePrices',codePrices)
    eur2btc_handler = CommandHandler('eur2btc', eur2btc)
    btc2eur_handler = CommandHandler('btc2eur', btc2eur)
    btc2sats_handler = CommandHandler('btc2sats', btc2sats)
    sats2btc_handler = CommandHandler('sats2btc', sats2btc)
    sats2eur_handler = CommandHandler('sats2eur', sats2eur)
    eur2sats_handler = CommandHandler('eur2sats', eur2sats)

    help_handler = CommandHandler('help', helper)
    
    application.add_handler(start_handler)
    application.add_handler(help_handler)    
    application.add_handler(price_handler)
    application.add_handler(info_handler)
    application.add_handler(codePrices_handler)
    application.add_handler(eur2btc_handler)
    application.add_handler(btc2eur_handler)
    application.add_handler(btc2sats_handler)
    application.add_handler(sats2btc_handler)
    application.add_handler(sats2eur_handler)
    application.add_handler(eur2sats_handler)

    application.run_polling()

