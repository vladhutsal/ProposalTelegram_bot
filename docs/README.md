## HTML to PDF Telegram bot

Bot for creating PDF file from styled HTML. User can fill the document fields via Telegram bot and get a PDF as an output.

## Prerequisites
### 1. Clone git repo:
```
git clone https://github.com/vladhutsal/HTML-to-PDF_TelegramBot.git
```
##### Open repository folder and go on.

### 2. Install Python3 and pip3:
**Linux:**
```
sudo apt-get install python3
```
**MacOS:**
```
brew install python3
```
pip3 is installed with Python3

## Installation:

### 1. Setup virtual environment:
- This will create a virtual env folder, named `env_tbot`:
```
python3 -m venv env_tbot
```
- Actiavate your virtual env:
```
source env_tbot/bin/activate
```
You should see a `(env_tbot)` appear at the beginning of your terminal prompt indicating that you are working inside the virtual environment.
- To leave virtual environment:
```
deactivate
```

### 2. Install dependencies:
```
pip3 install -r docs/requirements.txt
```

## Start bot:
### 1. Set token:
Create `credentials.py` file in the root directory and add the variable named `token`. Put your token, you've got from **BotFather** like this:
```
token = 'place to put your token'
```


### 2. Run Bot:
```
python3 telegram_bot.py
```
If everything is good, you shold see *UserWarning* about *CallbackQueryHandler tracking for every message* and the blinking cursor.
Now you can go to the bot in Telegram and initialize it using `/start` command.

