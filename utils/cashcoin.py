from typing import Union
from urllib.parse import unquote
from data import config
import aiohttp
from aiohttp_socks import ProxyConnector
from pyrogram import Client
from fake_useragent import UserAgent
import asyncio
import random
from pyrogram.raw.functions.messages import RequestWebView
from utils.core import logger
from utils.core.services import escape_html


class CashCoin:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: Union[str, None]) -> None:
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                'scheme': config.PROXY['TYPE']['TG'],
                'hostname': proxy.split(':')[1].split('@')[1],
                'port': proxy.split(':')[2],
                'username': proxy.split(':')[0],
                'password': proxy.split(':')[1].split('@')[0],
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru',
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def logout(self):
        await self.session.close()

    async def get_balance(self):
        await self.login()

        r = await (await self.session.get('https://click.cashcoin.game/api/profile', proxy=self.proxy)).json()

        balance = r.get('balance_coins')
        await asyncio.sleep(random.uniform(5, 7))

        return balance

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAY_BETWEEN_SWITCH_ACCOUNT))
        self.session.headers.pop('Authorization', None)

        await self.client.connect()

        await self.client.send_message("cashcoingame_bot", "/start")
        await asyncio.sleep(2)
        query = await self.get_tg_web_data()

        if not query:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.client.disconnect()
            await self.logout()
            return None

        json_data = {'web_app_data': query}

        resp = await self.session.post('https://click.cashcoin.game/api/auth/login', json=json_data)
        resp_json = await resp.json()

        self.session.headers['Authorization'] = 'Bearer ' + resp_json.get('access_token')
        return True

    async def send_taps(self):
        response_text = ''
        try:
            taps_count = random.randint(config.RANDOM_TAPS_COUNT[0], config.RANDOM_TAPS_COUNT[1])
            tg_web_data = await self.get_tg_web_data()

            json_data = {"count": taps_count, "web_app_data": tg_web_data}

            response = await self.session.post('https://click.cashcoin.game/api/click/apply', json=json_data)
            response_text = await response.text()
            response.raise_for_status()

            player_data = await response.json()

            return player_data
        except Exception as error:
            logger.error(f"{self.account} | Unknown error when Tapping: {escape_html(error)} | "
                         f"Response text: {escape_html(response_text)[:128]}...")
            await asyncio.sleep(3)

    async def get_tasks(self):
        resp = await self.session.get('https://click.cashcoin.game/api/bonus')
        return await resp.json()

    async def complete_task(self, task_name):
        url = f'https://click.cashcoin.game/api/bonus/{task_name}/apply'
        resp = await self.session.post(url)
        return await resp.json()

    async def get_tg_web_data(self):
        try:

            try:
                await self.client.connect()
            except:  # если клиент уже законнекчен в login
                ...

            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('cashcoingame_bot'),
                bot=await self.client.resolve_peer('cashcoingame_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://click.cashcoin.game/'
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user')[0]  # err
            user = query.split('&user=')[1].split('&auth_date')[0]
            auth_date = query.split('&auth_date=')[1].split('&hash')[0]
            hash_ = query.split('&hash=')[1]

            return f'query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}'
        except Exception as e:
            return None
