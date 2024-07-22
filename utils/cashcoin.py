from datetime import datetime
import time
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


class CashCoin:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: Union[str, None]) -> None:
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f'{config.PROXY['TYPE']['REQUESTS']}://{proxy}' if proxy else None
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
            lang_code='en',
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def logout(self):
        await self.session.close()

    async def stats(self):
        await self.login()

        r = await (await self.session.get('https://click.cashcoin.game/api/profile', proxy=self.proxy)).json()

        balance = r.get('balance_coins')
        referral_link = f'https://t.me/cashcoingame_bot/click?startapp={r.get('hash')}'

        await asyncio.sleep(random.uniform(5, 7))

        referrals = 0  # тут должно высчитываться число рефералов (хз где это взять из апи)

        await self.logout()
        await self.client.connect()
        me = await self.client.get_me()

        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', '') if self.proxy else ''

        return [phone_number, name, balance, referrals, referral_link, proxy]

    @staticmethod
    def iso_to_unix_time(iso_time: str):
        return int(datetime.fromisoformat(iso_time.replace('Z', '+00:00')).timestamp()) + 1

    @staticmethod
    def curr_time():
        return int(time.time())

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAY_BETWEEN_SWITCH_ACCOUNT))
        query = self.get_tg_web_data()

        if not query:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        json_data = {'web_app_data': query}

        resp = await self.session.post('https://click.cashcoin.game/api/auth/login', json_data=json_data)
        resp = await resp.json()

        self.session.headers['Authorization'] = 'Bearer ' + resp.get('access_token')
        return True

    async def get_tg_web_data(self):  # tg_web_data энивей нужна, нужна чтоб получить access_token (Authorization)
        try:
            await self.client.connect()

            peer = self.client.resolve_peer('cashcoingame_bot')

            web_view = self.client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://click.cashcoin.game/'
            ))

            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('&query_id=')[1].split('&user')[0]
            user = query.split('&user=')[1].split('&auth_date')[0]
            auth_date = query.split('&auth_date=')[1].split('&hash')[0]
            hash_ = query.split('&hash=')[1]

            return f'query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}'
        except:
            return None
