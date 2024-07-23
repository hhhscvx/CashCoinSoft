import asyncio
import random
from typing import Union
import time
from data import config
from utils.core import logger
from utils.cashcoin import CashCoin
from utils.core.services import escape_html


async def start(thread: int, session_name: str, phone_number: str, proxy: Union[str, None]):
    cashcoin = CashCoin(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await cashcoin.login():
        access_token_create_time = 0
        # TASKS:
        if config.COMPLETE_TASKS:
            tasks = await cashcoin.get_tasks()
            for task in tasks:
                task_name = task['key']
                if (task['is_done'] == 1):
                    logger.info(f'Thread {thread} | {account} | Task «{task["key"]}» already done')
                    continue
                elif (task_name in config.BLACKLIST_TASKS):
                    continue

                await cashcoin.complete_task(task_name)
                logger.success(f'Thread {thread} | {account} | Completed task «{task["key"]}»')
                await asyncio.sleep(1)

        while True:
            try:

                # TAPS:
                if time.time() - access_token_create_time >= 3600:
                    balance = await cashcoin.get_balance()  # login & get_data
                    access_token_create_time = time.time()

                player_data = await cashcoin.send_taps()

                if not player_data:
                    continue

                available_energy = player_data['available_coins']
                new_balance = player_data['balance_coins']
                calc_taps = abs(int(new_balance) - int(balance))
                balance = new_balance
                total = int(player_data['total_coins'])

                logger.success(f"{session_name} | Successful tapped! | "
                               f"Balance: {balance} (+{calc_taps}) | Total: {total}")

                if available_energy < config.MIN_AVAILABLE_ENERGY:
                    await cashcoin.logout()
                    random_sleep = random.randint(config.SLEEP_BY_MIN_ENERGY[0], config.SLEEP_BY_MIN_ENERGY[1])

                    logger.info(f"{account} | Minimum energy reached: {available_energy}")
                    logger.info(f"{account} | Sleep {random_sleep:,}s")

                    await asyncio.sleep(random_sleep)

                    access_token_create_time = 0

            except Exception as error:

                logger.error(f"{account} | Unknown error: {escape_html(error)}")
                raise error
                asyncio.sleep(2)

            else:
                sleep_between_taps = random.randint(config.DELAY_BETWEEN_TAPS[0], config.DELAY_BETWEEN_TAPS[1])

                logger.info(f"Sleep {sleep_between_taps}s")
                await asyncio.sleep(sleep_between_taps)

    else:
        await cashcoin.logout()
