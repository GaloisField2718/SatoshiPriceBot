# SatoshiPriceBot 🤖
This repository contains the code for the telegram Bot :  [SatoshiPriceBot](t.me/SatoshiPriceBot).

## Installation

For Telegram usage please find two major references behind : 

- [Introduction to the API · python-telegram-bot/python-telegram-bot Wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API)

- [Extensions Your first Bot · python-telegram-bot/python-telegram-bot Wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot)

### ⚠️  Features
Due to the oshi's feature which is fetching data from selenium you will be required to have Google chrome installed on your computer.
No worries, you can download as in [ubuntu server](https://askubuntu.com/questions/245041/how-do-i-install-chrome-on-a-server), [google_chrome [Wiki ubuntu-fr]](https://doc.ubuntu-fr.org/google_chrome) and for other OS you can download from [Official link](https://support.google.com/chrome/a/answer/9025903?hl=fr).

```
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
```

```
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
```

```
sudo apt-get update
sudo apt-get install google-chrome-stable
```

Verify : `google-chrome --version`


### Initialisation

```
git clone https://github.com/GaloisField2718/SatoshiPriceBot.git && cd SatoshiPriceBot
```

### Python env

I created this repo with `pipenv` as Package Manager [Pipenv: A Guide to the New Python Packaging Tool – Real Python](https://realpython.com/pipenv-guide/).

To run a Python environnement with `pipenv` :
 
```
pipenv shell
```

After this, like `npm` run :

```
pipenv install --ignore-pipfile
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

Information about [Runes](https://docs.ordinals.com/runes.html) from [Unisat runes market](https://unisat.io/runes/market). Floor selling order and marketcap based on current floor price on Unisat. 

Be free to update this repo and chat with me about improvement proposals. It's a small compilation of diverse code that I can did over the time in my coding journey. 
It's a pleasure to think about possible improvements. 

Next goal should be to handle errors which can occurs due to multiple browser and get calls. Display information on user side. 

## TODO

- Important: Handle errors during browser and requests calls. Provide a feedback to the user about the error. Provide tracking into loggin to be able to help the user if there is a problem in transportation or server side. 

- Fetch prices from [Atomical marketplace](https://atomicalmarket.com) like BRC-20.
    - I tried to copy paste the code for Unisat but it's not working like this. 
    - It should be quite easy !

- Use API of unisat instead of scrapping their website.

- Improve UX with :
   - making recommandations of available commands ;
   - if someone type a conversion command without amount : `/sats2eur` send a message to say : 'Enter the amount to convert' and after then make the conversion ;

- Improve HTML treatment which is not good for `/btcInfo` for example ;

- Make a containerisation of this code with `Docker`.

- Create a lightning invoice for `/support` command.


# Contact

[🐣 Galois Field](https://twitter.com/Blockcryptology)


[📩 mail](galoisfield2718@gmail.com)

[🤖 The Bot](https://t.me/SatoshiPriceBot)
