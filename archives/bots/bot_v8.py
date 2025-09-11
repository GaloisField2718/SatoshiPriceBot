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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler


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

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a custom handler
class CustomHandler(logging.StreamHandler):
    def emit(self, record):
        if "HTTP Request: POST https://api.telegram.org/bot" in record.getMessage() and "getUpdates" in record.getMessage():
            return
        super().emit(record)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a handler and set the formatter
handler = CustomHandler()
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


# ---------------------------------------------------------
#                   UTILS
# ---------------------------------------------------------

def format_number_with_dot(number):
    """Format a number using dot as decimal separator and no thousands separator"""
    if isinstance(number, str):
        # Replace comma with dot if it's being used as decimal separator
        if ',' in number and '.' not in number:
            number = number.replace(',', '.')
        # Remove any thousands separators
        number = number.replace(' ', '').replace(',', '')
        try:
            number = float(number)
        except ValueError:
            return str(number)
    
    # Format integer numbers without decimal places
    if isinstance(number, (int, float)):
        if number.is_integer():
            return str(int(number))
        
        # For very small numbers, ensure we show all zeros
        if abs(number) < 0.000001 and number != 0:
            # Count the number of zeros after the decimal point
            str_num = f"{number:.10f}"  # Use a high precision to count zeros
            decimal_part = str_num.split('.')[1]
            zero_count = 0
            for digit in decimal_part:
                if digit == '0':
                    zero_count += 1
                else:
                    break
            
            # If there are more than 9 zeros, show the number with all zeros
            if zero_count > 9:
                return f"{number:.{zero_count + 1}f}"
            else:
                # For numbers with 9 or fewer zeros, show 8 decimal places
                return f"{number:.8f}"
        
        # For floating point numbers, use standard decimal notation with dot
        # Remove trailing zeros but keep the decimal point if needed
        result = str(number)
        if '.' in result:
            # Split into integer and decimal parts
            int_part, dec_part = result.split('.')
            # Remove trailing zeros from decimal part
            dec_part = dec_part.rstrip('0')
            # Reconstruct the number
            if dec_part:
                result = f"{int_part}.{dec_part}"
            else:
                result = int_part
        return result
    
    return str(number)


def convert_str(data):
    printable_str = str(data).replace("{", "").replace("}", "")
    return printable_str
    
def normalize_input(value: str):
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


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

def create_inline_keyboard(buttons):
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in buttons])

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
    try:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            amount_input = float(format_number_with_dot(user_input))
            res = convert.btceur(amount_input, 0)
            formatted_input = "{:,.8f}".format(amount_input)
            formatted_res = format_number_with_dot("{:.2f}".format(res))
            message = f"{formatted_input} BTC = `{formatted_res}` EUR"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter the amount of Bitcoin you want to convert to Euros! Use /btc2eur amount."
            )
    except Exception as e:
        logging.error(f"Error during btc2eur conversion: {e} in {update}\n")
        message_error = f"Error during conversion: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


async def eur2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("eur2btc called \n")
    try:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            amount_input = float(format_number_with_dot(user_input))
            res = convert.btceur(amount_input, 1)
            formatted_input = format_number_with_dot("{:.2f}".format(amount_input))
            formatted_res = format_number_with_dot("{:.8f}".format(res))
            message = f"{formatted_input} EUR = `{formatted_res}` BTC"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter the amount in Euros you want to convert to Bitcoin! Use /eur2btc amount."
            )
    except Exception as e:
        logging.error(f"Error during eur2btc conversion: {e} in {update}\n")
        message_error = f"Error during conversion: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


async def btc2sat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            amount_input = float(format_number_with_dot(user_input))
            res = convert.satsbtc(amount_input, 1)
            formatted_input = format_number_with_dot("{:.8f}".format(amount_input))
            formatted_res = format_number_with_dot(str(int(res)))
            message = f"{formatted_input} BTC = `{formatted_res}` sats"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter the amount of Bitcoin you want to convert to satoshis! Use /btc2sat amount."
            )
    except Exception as e:
        logging.error(f"Error during btc2sat conversion: {e} in {update}\n")
        message_error = f"Error during conversion: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)

async def sat2btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("sat2btc called \n")
    try:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            amount_input = float(format_number_with_dot(user_input))
            res = convert.satsbtc(int(amount_input), 0)
            formatted_input = format_number_with_dot(str(int(amount_input)))
            formatted_res = format_number_with_dot("{:.8f}".format(res))
            message = f"{formatted_input} sats = {formatted_res} BTC"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter the amount of satoshis you want to convert to Bitcoin! Use /sat2btc amount."
            )
    except Exception as e:
        logging.error(f"Error during sat2btc conversion: {e} in {update}\n")
        message_error = f"Error during conversion: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


async def sat2eur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("sat2eur called \n")
    try:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            amount_input = float(format_number_with_dot(user_input))
            res = convert.satseur(int(amount_input), 0)
            formatted_input = format_number_with_dot(str(int(amount_input)))
            formatted_res = format_number_with_dot("{:.2f}".format(res))
            message = f"{formatted_input} sats = `{formatted_res}` EUR"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter the amount of satoshis you want to convert to Euros! Use /sat2eur amount."
            )
    except Exception as e:
        logging.error(f"Error during sat2eur conversion: {e} in {update}\n")
        message_error = f"Error during conversion: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


async def eur2sat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("eur2sat called \n")
    try:
        user_input = context.args[0] if context.args else None
        if user_input is not None:
            amount_input = float(format_number_with_dot(user_input))
            res = convert.satseur(amount_input, 1)
            formatted_input = format_number_with_dot("{:.2f}".format(amount_input))
            formatted_res = format_number_with_dot(str(int(res)))
            message = f"{formatted_input} EUR = `{formatted_res}` sats"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Please enter the amount in Euros you want to convert to satoshis! Use /eur2sat amount."
            )
    except Exception as e:
        logging.error(f"Error during eur2sat conversion: {e} in {update}\n")
        message_error = f"Error during conversion: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_error)


# ---------------------------------------------------------
#                       FEES
# ---------------------------------------------------------


async def fees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("fees called \n")
    try : 
        fees = Fees()
        message = f"No priority : {fees.no_priority}, Low priority : {fees.low_fees}, Mid priority : {fees.medium_fees}, High priority : {fees.max_fees} "
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
    keyboard = [
        [("Conversions", "category_conversions"), ("Fees", "category_fees")],
        [("Volumes", "category_volumes"), ("Runes", "category_runes")],
        [("General Info", "category_general_info"), ("Help", "category_help")],
        [("Contribute", "category_contribute")]
    ]
    reply_markup = create_inline_keyboard(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to SatoshiPriceBot! 🤖 \nChoose a category to explore:",
        reply_markup=reply_markup
    )


async def inline_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Conversion types with specific prompts
    conversion_prompts = {
        "convert_btc2eur": "Enter the amount of BTC to convert to EUR:",
        "convert_eur2btc": "Enter the amount of EUR to convert to BTC:",
        "convert_btc2sat": "Enter the amount of BTC to convert to Sats:",
        "convert_sat2btc": "Enter the amount of Sats to convert to BTC:",
        "convert_sat2eur": "Enter the amount of Sats to convert to EUR:",
        "convert_eur2sat": "Enter the amount of EUR to convert to Sats:",  
    }

    # Store the type of conversion selected and prompt for input
    if query.data in conversion_prompts:
        context.user_data["conversion_type"] = query.data
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=conversion_prompts[query.data]
        )

    # Navigation to other menus
    elif query.data == "category_conversions":
        await show_conversions_menu(update, context)
    elif query.data == "category_fees":
        await show_fees_menu(update, context)
    elif query.data == "category_volumes":
        await show_volumes_menu(update, context)
    elif query.data == "category_runes":
        await show_runes_menu(update, context)
    elif query.data == "category_general_info":
        await show_general_info_menu(update, context)
    elif query.data == "category_help":
        await helper(update, context)
    elif query.data == "start":
        await start(update, context)



async def handle_conversion_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check for rune action first
        rune_action = context.user_data.pop("rune_action", None)
        if rune_action:
            user_input = update.message.text.strip()
            rune_names = user_input.split()
            for rune in rune_names:
                if rune_action == "runes_info":
                    message = fetch_runes.info_message(rune)
                elif rune_action == "runes_floor_price":
                    message = fetch_runes.floor_listing(rune)
                elif rune_action == "runes_market_cap":
                    btc_marketcap, usd_marketcap = fetch_runes.get_marketcap(rune)
                    message = f"{rune}:\nMarket Cap: {btc_marketcap} BTC / ${usd_marketcap}"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            await show_runes_menu(update, context)  # Return to Runes menu
            return

        # Handle conversions
        conversion_type = context.user_data.pop("conversion_type", None)
        if conversion_type:
            try:
                # Format input number first
                input_text = update.message.text.strip()
                formatted_input = format_number_with_dot(input_text)
                amount = float(formatted_input)
                
                if conversion_type == "convert_btc2eur":
                    result = convert.btceur(amount, 0)
                    formatted_result = format_number_with_dot("{:.2f}".format(result))
                    formatted_amount = format_number_with_dot("{:.8f}".format(amount))
                    message = f"{formatted_amount} BTC = `{formatted_result}` EUR"
                    await update.message.reply_text(
                        text=message,
                        parse_mode='Markdown'
                    )
                elif conversion_type == "convert_eur2btc":
                    result = convert.btceur(amount, 1)
                    formatted_result = format_number_with_dot("{:.8f}".format(result))
                    formatted_amount = format_number_with_dot("{:.2f}".format(amount))
                    message = f"{formatted_amount} EUR = `{formatted_result}` BTC"
                    await update.message.reply_text(
                        text=message,
                        parse_mode='Markdown'
                    )
                elif conversion_type == "convert_btc2sat":
                    result = convert.satsbtc(amount, 1)
                    formatted_result = format_number_with_dot(str(int(result)))
                    formatted_amount = format_number_with_dot("{:.8f}".format(amount))
                    message = f"{formatted_amount} BTC = `{formatted_result}` Sats"
                    await update.message.reply_text(
                        text=message,
                        parse_mode='Markdown'
                    )
                elif conversion_type == "convert_sat2btc":
                    result = convert.satsbtc(int(amount), 0)
                    formatted_result = format_number_with_dot("{:.8f}".format(result))
                    formatted_amount = format_number_with_dot(str(int(amount)))
                    message = f"{formatted_amount} Sats = `{formatted_result}` BTC"
                    await update.message.reply_text(
                        text=message,
                        parse_mode='Markdown'
                    )
                elif conversion_type == "convert_sat2eur":
                    result = convert.satseur(int(amount), 0)
                    formatted_result = format_number_with_dot("{:.2f}".format(result))
                    formatted_amount = format_number_with_dot(str(int(amount)))
                    message = f"{formatted_amount} Sats = `{formatted_result}` EUR"
                    await update.message.reply_text(
                        text=message,
                        parse_mode='Markdown'
                    )
                elif conversion_type == "convert_eur2sat":
                    result = convert.satseur(amount, 1)
                    formatted_result = format_number_with_dot(str(int(result)))
                    formatted_amount = format_number_with_dot("{:.2f}".format(amount))
                    message = f"{formatted_amount} EUR = `{formatted_result}` Sats"
                    await update.message.reply_text(
                        text=message,
                        parse_mode='Markdown'
                    )
                await show_conversions_menu(update, context)  # Return to conversions menu
                return
            except ValueError:
                await update.message.reply_text("Invalid input. Please enter a valid number.")
                return

        # Default fallback
        await update.message.reply_text("Invalid input. Please use the menu options.")
    except Exception as e:
        logging.error(f"Error in handle_conversion_input: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")




async def show_conversions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [("BTC to EUR", "convert_btc2eur"), ("EUR to BTC", "convert_eur2btc")],
        [("BTC to Sats", "convert_btc2sat"), ("Sats to BTC", "convert_sat2btc")],
        [("Sats to EUR", "convert_sat2eur"), ("EUR to Sats", "convert_eur2sat")],
        [("🏠Back to Main Menu", "start")]
    ]
    reply_markup = create_inline_keyboard(keyboard)
    message = (
        "🔄Choose an option:"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

async def show_fees_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [("📈Mempool Fees", "fetch_fees"), ("🚀Get Max Fees", "fetch_max_fees")],
        [("🏠Back to Main Menu", "start")]
    ]
    reply_markup = create_inline_keyboard(keyboard)
    message = "Choose an option:"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

async def handle_fees_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Safely answer the query
    try:
        await query.answer()  # Acknowledge the query to avoid timeout issues
    except telegram.error.BadRequest as e:
        logging.warning(f"Failed to answer callback query: {e}")

    # Handle the callback data
    if query.data == "fetch_fees":
        logging.info("Calling fees function")
        await fees(update, context)
    elif query.data == "fetch_max_fees":
        logging.info("Calling max_fees function")
        await max_fees(update, context)
    elif query.data == "start":
        logging.info("Navigating back to main menu")
        await start(update, context)
        return  # Exit here to prevent showing the fees menu again
    
    # After processing, show the Fees Menu again
    await show_fees_menu(update, context)


async def show_volumes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [("Major Volumes", "major_volumes"), ("Binance Volumes", "binance_volumes")],
        [("Kraken Volumes", "kraken_volumes")],
        [("🏠Back to Main Menu", "start")]
    ]
    reply_markup = create_inline_keyboard(keyboard)
    message = "Choose an option to get detailed volume data:"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

async def handle_volumes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Handle the callback data
    if query.data == "major_volumes":
        await major_volumes(update, context)
    elif query.data == "binance_volumes":
        await binance_volumes(update, context)
    elif query.data == "kraken_volumes":
        await kraken_volumes(update, context)
    elif query.data == "start":
        await start(update, context)
        return  # Exit here to prevent showing the volumes menu again

    # After processing, show the Volumes Menu again
    await show_volumes_menu(update, context)


async def show_general_info_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [("Bitcoin Price", "btc_price"), ("Bitcoin Info", "btc_info")],
        [("Bitcoin ATH", "btc_ath"), ("Movements", "btc_movements")],
        [("Supply", "btc_supply"), ("Public Engagement", "btc_public")],
        [("Dev Engagement", "btc_dev")],
        [("🏠Back to Main Menu", "start")]
    ]
    reply_markup = create_inline_keyboard(keyboard)
    message = "Choose an option to get Bitcoin-related information:"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=reply_markup
    )

async def handle_general_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Handle the callback data
    if query.data == "btc_price":
        await btcPrice(update, context)
    elif query.data == "btc_info":
        await btcInfo(update, context)
    elif query.data == "btc_ath":
        await btcATH(update, context)
    elif query.data == "btc_movements":
        await btcMovements(update, context)
    elif query.data == "btc_supply":
        await btcSupply(update, context)
    elif query.data == "btc_public":
        await btcPublicEngagement(update, context)
    elif query.data == "btc_dev":
        await btcDevEngagement(update, context)
    elif query.data == "start":
        await start(update, context)
        return  # Exit here to prevent showing the general info menu again

    # After processing, show the General Info Menu again
    await show_general_info_menu(update, context)

async def show_runes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [("Rune Info", "runes_info"), ("Rune Floor Price", "runes_floor_price")],
        [("Rune Market Cap", "runes_market_cap"), ("General Rune Listings", "runes_listings")],
        [("🏠Back to Main Menu", "start")]
    ]
    reply_markup = create_inline_keyboard(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Choose an option to get details about Runes.",
        reply_markup=reply_markup
    )


async def handle_runes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "runes_info":
        context.user_data["rune_action"] = "runes_info"
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Enter the name of the Rune(s) (e.g., `satoshi.nakamoto`) to get basic information:"
        )
    elif query.data == "runes_floor_price":
        context.user_data["rune_action"] = "runes_floor_price"
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Enter the name of the Rune(s) to get the floor price listing:"
        )
    elif query.data == "runes_market_cap":
        context.user_data["rune_action"] = "runes_market_cap"
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Enter the name of the Rune(s) to get market cap information:"
        )
    elif query.data == "runes_listings":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Fetching general Rune listings from Unisat...")
        message = fetch_runes.get_all_listings()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        await show_runes_menu(update, context)  # Show menu again
        return
    elif query.data == "start":
        await start(update, context)
        return

    # Don't show the Runes menu again yet; wait for user input



async def handle_rune_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rune_action = context.user_data.get("rune_action")
    user_input = update.message.text.strip()
    rune_names = user_input.split()

    try:
        if rune_action == "runes_info":
            for rune in rune_names:
                message = fetch_runes.info_message(rune)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        elif rune_action == "runes_floor_price":
            for rune in rune_names:
                message = fetch_runes.floor_listing(rune)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        elif rune_action == "runes_market_cap":
            for rune in rune_names:
                btc_marketcap, usd_marketcap = fetch_runes.get_marketcap(rune)
                message = f"{rune}: {btc_marketcap} BTC / ${usd_marketcap} USD"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        context.user_data["rune_action"] = None  # Clear the action
        await show_runes_menu(update, context)  # Show the Runes menu again
    except Exception as e:
        logging.error(f"Error processing Rune input: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again.")


async def show_contribute_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    logging.info(f"Contribute button clicked by {query.from_user.username}")
    
    message = (
        " 💡 *Got suggestions or feedback?* \n"
        "Feel free to contact [@Dev\\_block](https://t.me/Dev\\_block) directly\.\n\n"
        " ₿ *Want to contribute to the bot's development?* \n"
        "Check out the repo here: [SatoshiPriceBot GitHub Repository](https://github.com/GaloisField2718/SatoshiPriceBot/tree/main)\n\n"
        "For more information, see the */help* message\."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message,parse_mode="MarkdownV2")
    await support(update, context)


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
    # Safely handle both message and callback query updates
    if update.message:
        username = update.message.chat.username
        chat_id = update.message.chat.id
    elif update.callback_query:
        username = update.callback_query.from_user.username
        chat_id = update.callback_query.message.chat_id
    else:
        username = "unknown"
        chat_id = None

    logging.info(f"support called by {username}\n")

    if chat_id:
        message = ("Want to support the bot's hosting⁉️\n\nYou can send some sats at 👉bc1qxxuuxmlp3wxuyn6uuqw448nzaafuqdxc076m9k👈.\n\nI'm hosted at Hostinger and payment can be done in Bitcoin ! So, your money will directly go to Hostinger 🙃.\n\nThank you for your support!"

        )
        await context.bot.send_message(chat_id=chat_id, text=message)

        # Attempt to send the QR code
        pic = os.path.join(os.getcwd(), 'qr_generator', 'qr_myaddress.png')
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=pic)
        except FileNotFoundError:
            logging.error("QR code image not found.")
            await context.bot.send_message(
                chat_id=chat_id,
                text=" ⚠️ Sorry, the QR code image is currently unavailable. Please use the BTC address above."
            )


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [("Conversions", "category_conversions"), ("Fees", "category_fees")],
        [("Volumes", "category_volumes"), ("Runes", "category_runes")],
        [("General Info", "category_general_info"), ("🏠Back to Main Menu", "start")]
    ]
    reply_markup = create_inline_keyboard(keyboard)

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

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_help, reply_markup=reply_markup)


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
    callback_handler = CallbackQueryHandler(inline_callback_handler)
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_conversion_input)
    fees_menu_handler = CallbackQueryHandler(handle_fees_callback, pattern="fetch_fees|fetch_max_fees|start")
    volumes_menu_handler = CallbackQueryHandler(handle_volumes_callback, pattern="major_volumes|binance_volumes|kraken_volumes|start")
    general_info_menu_handler = CallbackQueryHandler(handle_general_info_callback, pattern="btc_price|btc_info|btc_ath|btc_movements|btc_supply|btc_public|btc_dev|start")
    runes_menu_handler = CallbackQueryHandler(handle_runes_callback, pattern="runes_info|runes_floor_price|runes_market_cap|runes_listings|start")
    contribute_menu_handler = CallbackQueryHandler(show_contribute_message, pattern="category_contribute")
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

    application.add_handler(contribute_menu_handler)
    application.add_handler(runes_menu_handler)
    application.add_handler(general_info_menu_handler)
    application.add_handler(volumes_menu_handler)
    application.add_handler(fees_menu_handler)
    application.add_handler(callback_handler)
    application.add_handler(message_handler)
   
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