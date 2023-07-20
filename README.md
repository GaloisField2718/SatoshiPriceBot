# SatoshiPriceBot 🤖
This repository contains the code for the telegram Bot :  [SatoshiPriceBot](t.me/SatoshiPriceBot).

## Installation

For Telegram usage please find two major references behind : 

- [Introduction to the API · python-telegram-bot/python-telegram-bot Wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API)

- [Extensions Your first Bot · python-telegram-bot/python-telegram-bot Wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot)

### Initialisation
```
git clone https://github.com/GaloisField2718/telegram_bot.git && cd telegram_bot
```

### Python env

I created this repo with `pipenv` as Package Manager [Pipenv: A Guide to the New Python Packaging Tool – Real Python](https://realpython.com/pipenv-guide/).

To run a Python environnement with `pipenv` :
 
```
pipenv shell
```

After this, like `npm` run :

```
pipenv install
```

It will install every required dependancies.

### Bot token

After creating your bot with [BotFather](https://t.me/botfather), take its token `numbers:Letters`, create a file `.env` and insert : 
```
KEY=numbers:Letters
```

## Run

After installation, you can run your bot with : 

```
cd src && python3 bot_v2.py
```

Warning be sure to run `pipenv shell` if you are using a new terminal session.

  

# Add new commands

To add new commands you should 

1) create a new function : 
```python
async def your_function(update: Update, context: ContextTypes.DEFAULT_TYPE) : 
    #Some actions

```

2) I recommend you to add your new function in `helper` function. 
    a) add `message_your_function = "/your_function : What my incredible function do. Example : \n "`
    b) add it in the global helper message `message_help += message_your_function`

3) Create a handler for your function
```python
your_function_handler = CommandHandler('your_function', your_function) # You can name differently the command for the user and your function itself

application.add_handler(your_function_handler)
```

And... That's it. You created your first new command in this bot. 

## Updates

The last update changed fetch prices. Before I used `python-binance`, but now I use [CoinGecko API](https://www.coingecko.com/fr/api/documentation).

I added, many different information about Bitcoin from CoinGecko.

Please be free to update this repo and chat with me about improvement proposals. It's a small compilation of diverse code that I can did over the time in my coding journey. 
It's a pleasure to think about possible improvements. 

For the next, I have to think about a cointainerisation with `Docker` to be able to run on any server, very quickly ; without manual installation.

## TODO

- Improve volumes visualisation ;
- Improve UX with :
   - making recommandations of available commands ;
   - if someone type a conversion command without amount : `/sats2eur` send a message to say : 'Enter the amount to convert' and after then make the conversion ;
- Improve HTML treatment which is not good for `/btcInfo` for example ;
- Make a containerisation of this code with `Docker`.


# Contact

[🐣 Galois Field](https://twitter.com/Blockcryptology)


[📩 mail](galoisfield2718@gmail.com)

