
import asyncio
import os
from pyrogram import Client
from data import config
from utils.core import (save_accounts_list_to_file,
                        save_to_json, load_from_json,
                        logger)


class Accounts:
    def __init__(self) -> None:
        self.workdir = config.WORKDIR
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    @staticmethod
    def get_available_accounts(sessions: list):  # Возвращает аккаунты, к которым есть сессия
        accounts_from_json = load_from_json('sessions/accounts.json')

        if not accounts_from_json:
            raise ValueError("Have not accounts in sessions/accounts.json\nYou need to create sessions first")

        available_accounts = []
        for session in sessions:
            for saved_accounts in accounts_from_json:
                if saved_accounts['session'] == session:
                    available_accounts.append(saved_accounts)
                    break  # Аккаунт к данной сессии найден, ищем следующую
        return available_accounts

    async def check_valid_account(self, account: dict):  # проверка коннекта аккаунта
        session_name, phone_number, proxy = account.values()

        try:
            proxy_dict = {
                'scheme': config.PROXY['TYPE']['TG'],
                'hostname': proxy.split(':')[1].split('@')[1],
                'port': int(proxy.split(':')[2]),
                'username': proxy.split(':')[0],
                'password': proxy.split(':')[1].split('@')[0],
            } if proxy else None

            client = Client(session_name, self.api_id, self.api_hash, workdir=self.workdir,
                            phone_number=phone_number, proxy=proxy_dict)

            connect = asyncio.wait_for(client.connect(), config.CLIENT_CONNECT_TIMEOUT)

            if connect:
                await client.get_me()
                await client.disconnect()
                return account
            else:
                await client.disconnect()
        except:
            pass

    async def check_valid_accounts(self, accounts: list):

        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(self.check_valid_account(account)))

        v_accounts = asyncio.gather(*tasks)

        valid_accounts = [account for account, is_valid in zip(
            accounts, v_accounts) if is_valid]  # is_valid = check_valid вернул аккаунт
        invalid_accounts = [account for account, is_valid in zip(
            accounts, v_accounts) if not is_valid]  # not is_valid = check_valid вернул None
        logger.success(f"Successful check! | Valid accounts: {len(valid_accounts)}; Invalid: {len(invalid_accounts)}")

        return valid_accounts, invalid_accounts

    async def get_accounts(self):
        sessions = self.pars_sessions()
        available_accounts = self.get_available_accounts(sessions)

        if not available_accounts:
            raise ValueError("Have not available accounts!")
        else:
            logger.success(f"Found available accounts: {len(available_accounts)}.")

        valid_accounts, invalid_accounts = self.check_valid_accounts(available_accounts)

        if invalid_accounts:
            save_accounts_list_to_file(f'{self.workdir}invalid_accounts.txt', invalid_accounts)
            logger.info(f"Saved {len(invalid_accounts)} invalid account(s) in {self.workdir}invalid_accounts.txt")

        if not valid_accounts:
            raise ValueError("Have not valid sessions")
        else:
            return valid_accounts

    def pars_sessions(self):
        sessions = []
        for file in os.listdir(self.workdir):
            if file.endswith('.session'):
                sessions.append(file.replace('.session', ''))

        logger.info(f"Searched sessions: {len(sessions)}.")
        return sessions

    async def create_sessions(self):
        while True:
            session_name = input("\nInput the name of the session (press Enter to exit): ")
            if not session_name:
                return

            proxy = input('Input the proxy in the format login:password@ip:port (press Enter to use without proxy): ')

            if proxy:
                client_proxy = {
                    'scheme': config.PROXY['TYPE']['TG'],
                    'hostname': proxy.split(':')[1].split('@')[1],
                    'port': int(proxy.split(':')[2]),
                    'username': proxy.split(':')[0],
                    'password': proxy.split(':')[1].split('@')[0],
                }
            else:
                client_proxy, proxy = None, None

            phone_number = (input("Input the phone number of the account: ")).replace(' ', '')
            phone_number = '+' + phone_number if not phone_number.startswith('+') else phone_number

            client = Client(name=session_name, api_id=self.api_id, api_hash=self.api_hash,
                            workdir=self.workdir, phone_number=phone_number, proxy=client_proxy, lang_code='ru')

            async with client:
                me = await client.get_me()

            save_to_json(f'{self.workdir}accounts.json', dict_={
                "session_name": session_name,
                "phone_number": phone_number,
                "proxy": proxy,
            })
            logger.success(f"Added an account {me.username} ({me.first_name}) | {me.phone_number}")
