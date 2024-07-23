from dotenv import load_dotenv
import os

load_dotenv()

API_ID = int(os.getenv("API_ID"))  # Напишите сюда свой api_id с my.telegram.org
API_HASH = str(os.getenv("API_HASH"))  # Напишите сюда свой api_hash с my.telegram.org


PROXY = {
    "USE_PROXY_FROM_FILE": False,
    "PROXY_PATH": "data/proxy.txt",
    "TYPE": {
        "TG": "socks5",
        "REQUESTS": "socks5"
    }
}

# Выполнять задания при каждом запуске софта (отключите после первого выполнения)
COMPLETE_TASKS = True

BLACKLIST_TASKS = ['invite-friend']

WORKDIR = "sessions/"  # куда сохраняются сессии

DELAY_BETWEEN_SWITCH_ACCOUNT = [5, 15]
DELAY_BETWEEN_TAPS = [10, 25]

RANDOM_TAPS_COUNT = [50, 200]

CLIENT_CONNECT_TIMEOUT = 30

MIN_AVAILABLE_ENERGY = 100
SLEEP_BY_MIN_ENERGY = [1800, 2400]

BOLD = '\033[1m'

END = '\033[0m'


SOFT_INFO = f"""{f'{BOLD}CashCoinBot{END}'.center(40)}
Complete Tasks & Auto Taps;

The soft also collects statistics on accounts and uses proxies from {f"the {PROXY['PROXY_PATH']} file" if PROXY['USE_PROXY_FROM_FILE'] else "the accounts.json file"}
"""
