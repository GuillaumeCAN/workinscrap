# WorkinScrap

A small Python tool to automate scraping data from WorkinLive and filling MQC forms. Designed and developed by **Abraxas**.

![Install guide][#Installation]

## DISCLAIMER
WorkinScrap is an application designed for an educational purpose only!
It is in no way designed to cheat or falsify results!
This project's sole purpose is to improve programming and web scraping skills. I dissociate myself from any use for cheating purposes.

Best regards - **Abraxas**

![logo](https://i.ibb.co/7J36Ch6X/logo.png)

## Features

This project is coded in Python 3.12 and uses Selenium as well as API requests to Gemini AI.

- Authenticate to WorkinLive (manual credentials, .env variables will come in future updates)
- Scrape required data (user assignments, times, metadata)
- Populate and submit MQC forms automatically
- Idling account to increase the time spent on the plateform


## Requirements

- Python 3.8+
- pip
- A browser driver (e.g., chromedriver, firefox)

**Python packages:**
- requests
- selenium / webbrowser
- rich
- pyfiglet
- prompt_toolkit
- time / datetime
- threading
- google.generativeai


## Installation
First you need to download the project by downloading the last release or :

```
git clone git@github.com:GuillaumeCAN/workinscrap.git
```

Go to the project's directory and install all the necessary lib :

```
pip install -r requirements.txt
```

You are now ready to use WorkinScrap!
To start the script, simply use :

```
python3 main.py
```


## Configuration
To make sure you can fully use WorkinScrap, you will have to set your Gemini API key in the `config.py:

```python
APP_NAME = "WorkinScrap"  
AUTHOR = "Abraxas"  
VERSION = "1.0.3"  
  
GITHUB_REPO = "https://github.com/GuillaumeCAN/workinscrap"  
  
LOGIN_URL = "https://www.workinlive.school/login"  
  
USERNAME_SELECTOR = "/html/body/div/div/div/div/div[2]/form/div[1]/div/input"  
PASSWORD_SELECTOR = "/html/body/div/div/div/div/div[2]/form/div[2]/div/input"  
SUBMIT_BUTTON_SELECTOR = "/html/body/div/div/div/div/div[2]/form/button/span"  
  
SUCCESS_ELEMENT_SELECTOR = "/html/body/div/div/div/div[1]/div/div/div[2]/div/h1"  
  
# USER  
USER_NAME = "/html/body/div/div/header/div[1]/div/ul/li[3]/div/span"  
USER_TIME_SPENT = "/html/body/div/div/div/main/section/div/div/div/div[1]/div/div/div[1]/div/div/div/div[2]/div[1]/strong"  
COURSE_LIST_UL = "/html/body/div/div/div/main/section/div/div/div/div[1]/div/ul"  
MODULE_CARD_LIST = "/html/body/div/div/div/main/section/div/div"  
BACK_TO_COURSE_BTN = "/html/body/div/div/header/div[1]/button/span[1]"  
  
API_KEY = "YOUR API KEY HERE"
```

**Please do not modify anything except API_KEY**
The remaining settings can be modified in the Configuration tab of the script's main menu. 

Several configuration options are still under development. For now, the driver is always visible and firefox is the default driver but a headless mode will come in the future updates as well as a driver selector, so stay tunned :p


## Usage

You can navigate through the different menus using the arrow keys. Sometimes the script is slow to load the menus due to WorkinLive's completely messed-up code, but don't worry, if the script crashes, you will be noticed.

Sometimes, even Gemini cannot get a full correct score while completing MQC... So don't be afraid if you get 4/5, this is just the proof that WorkinLive is shit.

![main-menu.png](https://i.ibb.co/20bxb3G4/Capture-d-cran-2025-11-13-121638.png)

## Logging & Output

No personal information, tokens, or credentials are stored or sent.
A log window is currently visible in the script, but in a future update it may disappear and be replaced by a more user-friendly interface.


## Bugs and report

During your trip through the script, you may encounter some bugs / crashes. Sometime it's just a one-shot bug that will no longer appear because... you know... workinlive... But sometimes its a persistent bug / crashes. In this case, feel free to report any using the Issues tab on Github, or by sending my an email with all the possible details.


## License

GNU GENERAL PUBLIC LICENSE (e.g., MIT) in LICENSE file.