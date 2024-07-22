API_ID = 1234
API_HASH = "asdf9876"


PROXY = {
    "USE_PROXY_FROM_FILE": False,
    "PROXY_PATH": "data/proxy.txt",
    "TYPE": {
        "TG": "socks5",
        "REQUESTS": "socks5"
    }
}

BLACKLIST_TASKS = ['invite-friend']

WORKDIR = "sessoins/"  # куда сохраняются сессии

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
