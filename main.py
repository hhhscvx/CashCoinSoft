import asyncio
from data import config
from utils.core.telegram import Accounts
import os

from utils.starter import start


async def main():
    print(f"{config.BOLD}CashCoin Soft{config.END}".center(40))
    action = int(input("Select action:\n0. About soft\n1. Start soft\n2. Get statistics\n3. Create sessions\n\n> "))

    if action == 0:
        print(config.SOFT_INFO)
        return

    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    if config.PROXY['USE_PROXY_FROM_FILE']:
        if not os.path.exists(config.PROXY['PROXY_PATH']):
            with open(config.PROXY['PROXY_PATH'], 'w') as f:
                f.write("")
    else:
        if not os.path.exists("sessions/accounts.json"):
            with open("sessions/accounts.json", "w") as file:
                file.write("[]")

    if action == 3:
        await Accounts().create_sessions()

    if action == 2:
        print("Без статистики брат")

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []

        for thread, account in enumerate(accounts):  # thread = какой аккаунт по очереди
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(start(thread=thread, session_name=session_name,
                                                   phone_number=phone_number, proxy=proxy)))

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
