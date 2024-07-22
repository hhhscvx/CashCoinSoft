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

        while True:
            try:
                # TASKS:
                tasks = await cashcoin.get_tasks()
                for task in tasks:
                    task_name = task['key']
                    if (task_name in config.BLACKLIST_TASKS) or (task['is_done'] == 1):
                        continue

                    await cashcoin.complete_task(task_name)
                    logger.success(f'Thread {thread} | {account} | Completed task «{task["description"]}»')
                    await asyncio.sleep(1)

                # TAPS:
                if time.time() - access_token_create_time >= 3600:
                    profile_data = await cashcoin.stats()  # login & get_data
                    access_token_create_time = cashcoin.curr_time()

                    balance = profile_data[2]

                player_data = await cashcoin.send_taps()

                if not player_data:
                    continue

                available_energy = player_data['available_coins']
                new_balance = player_data['balance_coins']
                calc_taps = abs(new_balance - balance)
                balance = new_balance
                total = player_data['total_coins']

                logger.success(f"{account} | Successful tapped! | "
                               f"Balance: <c>{balance:,}</c> (<g>+{calc_taps:,}</g>) | Total: <e>{total:,}</e>")

                if available_energy < config.MIN_AVAILABLE_ENERGY:
                    # await self.session.close ?
                    random_sleep = random.randint(config.SLEEP_BY_MIN_ENERGY[0], config.SLEEP_BY_MIN_ENERGY[1])

                    logger.info(f"{account} | Minimum energy reached: {available_energy}")
                    logger.info(f"{account} | Sleep {random_sleep:,}s")

                    await asyncio.sleep(random_sleep)

                    access_token_create_time = 0

            except Exception as error:
                logger.error(f"{account} | Unknown error: {escape_html(error)}")
                asyncio.sleep(2)

            else:
                sleep_between_taps = random.randint(config.DELAY_BETWEEN_TAPS[0], config.DELAY_BETWEEN_TAPS[1])

                logger.info(f"Sleep {sleep_between_taps}s")
                await asyncio.sleep(sleep_between_taps)

    else:
        await cashcoin.logout()
