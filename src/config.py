import os
from datetime import datetime
import pytz

# Email
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT = "andrzej.bojko94@gmail.com"

# APIs
FOOTBALL_DATA_TOKEN = os.getenv("FOOTBALL_DATA_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Timezone
WARSAW = pytz.timezone("Europe/Warsaw")

# Competitions we care about (football-data.org free tier codes)
# https://www.football-data.org/documentation/api
COMPETITIONS = [
    # Główne (lepsza jakość)
    "PL",   # Premier League
    "PD",   # La Liga
    "BL1",  # Bundesliga
    "SA",   # Serie A
    "FL1",  # Ligue 1
    "CL",   # Champions League
    "EL",   # Europa League
    "DED",  # Eredivisie
    "PPL",  # Primeira Liga
    "ELC",  # Championship

    # Inne ligi (słabsza jakość danych)
    "BSA",  # Brasileirão
    "MLS",  # MLS
    "SPL",  # Scottish Premiership
    "CLI",  # Copa Libertadores (jeśli dostępne)
]

# Odds range for main list
MIN_ODDS = 1.70
MAX_ODDS = 2.30
HIGH_ODDS_MIN = 3.00

# How many tips
MAIN_TIPS = 15
VALUE_TIPS = 5

def today_warsaw() -> str:
    return datetime.now(WARSAW).strftime("%Y-%m-%d")
