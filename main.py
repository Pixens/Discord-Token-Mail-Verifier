import tls_client
import base64
import json
import random
import yaml
import itertools
import secrets
import concurrent.futures

from utils import Logger
from utils import Utils
from utils import KopeechkaApi


__tokens__ = itertools.cycle(open('./input/tokens.txt', 'r').read().splitlines())
__config__ = yaml.safe_load(open('config.yml', 'r').read())
__proxies__ = open('./input/proxies.txt', 'r').read().splitlines()
__build_number__ = Utils.get_build_number()


class Discord:
    def __init__(self):
        self.fulltoken = next(__tokens__)
        self.token = self.fulltoken.split(':')[-1]
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        self.session = tls_client.Session(
            client_identifier='chrome_119',
            random_tls_extension_order=True
        )
        self.cookies = ''
        self.xsuper = self.build_xsuper()
        self.session.headers = {
            "Accept": "*/*",
            "Accept-language": f"en-GB,en;q=0.9",
            "Authorization": self.token,
            "Content-type": "application/json",
            "Cookie": self.cookies,
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not.A/Brand";v="24", "Chromium";v="119", "Google Chrome";v="119"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.user_agent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": 'en-GB',
            "X-Super-Properties": self.xsuper
        }
        if __config__['proxies']:
            self.session.proxies = f"{__config__['proxy_type']}://{random.choice(__proxies__)}"
        self.set_cookies()
    
    def build_xsuper(self):
        properties = {
            "os": 'Windows',
            "browser": 'Chrome',
            "device": "",
            "system_locale": 'en-GB',
            "browser_user_agent": self.user_agent,
            "browser_version": '119.0.0.0',
            "os_version": "10",
            "referrer": "https://discord.com",
            "referring_domain": "discord.com",
            "referrer_current": "https://discord.com",
            "referring_domain_current": "discord.com",
            "release_channel": "stable",
            "client_build_number": __build_number__,
            "client_event_source": None
        }
        return base64.b64encode(json.dumps(properties, separators=(',', ':')).encode("utf-8")).decode()

    def set_cookies(self, tries=0):
        if tries > 3:
            raise Exception(f'Error getting cookies | {self.token}')
            return
        try:
            response = self.session.get('https://discord.com/app')
        except tls_client.exceptions.TLSClientExeption:
            return self.set_cookies(tries=tries+1)
        for cookie in response.cookies:
            self.cookies += f"{cookie.name}={cookie.value};"
        if not self.cookies:
            return self.set_cookies(tries=tries+1)
        self.cookies += 'locale=en-GB;'
        self.session.headers.update({'Cookie': self.cookies})

    def add_email(self, mail, tries=0):
        if tries > 3:
            raise Exception(f'Error adding mail | {self.token}')
            return
        try:
            password = self.fulltoken.split(':')[1]
        except IndexError:
            password = secrets.token_hex(16)
        payload = {
            'email': mail,
            'password': password
        }
        try:
            response = self.session.patch('https://discord.com/api/v9/users/@me', json=payload)
        except tls_client.exceptions.TLSClientExeption:
            return self.add_email(mail, tries=tries+1)
        if response.status_code == 200:
            Utils.remove(self.fulltoken, './input/tokens.txt')
            self.token = response.json()['token']
            self.fulltoken = f"{mail}:{password}:{self.token}"
            Utils.write(self.fulltoken, './output/claimed.txt')
            Logger.info(f'Added mail | {self.token}')
            return True
        else:
            Logger.error(f'Failed to add mail | {self.token}')
            return False
    
    def verify_email(self, verification_token, tries=0):
        if tries > 3:
            raise Exception(f'Error verifing email | {self.token}')
            return
        payload = {
            'token': verification_token
        }
        try:
            response = self.session.post('https://discord.com/api/v9/auth/verify', json=payload)
        except tls_client.exceptions.TLSClientExeption:
            return self.verify_email(verification_token, tries=tries+1)
        if response.status_code == 200:
            Utils.remove(self.fulltoken, './output/claimed.txt')
            self.token = response.json()['token']
            self.fulltoken = f"{self.fulltoken.split(':')[0]}:{self.fulltoken.split(':')[1]}:{self.token}"
            Utils.write(self.fulltoken, './output/verified.txt')
            Logger.info(f'Verified email | {self.token}')
            return True
        else:
            Logger.error(f'Failed to verify email | {self.token}')
            return False
    
    def run(self):
        try:
            KopcheekaApi = KopeechkaApi()
            response = KopcheekaApi.get_email()
            added = self.add_email(response.mail)
            if added:
                verification_token = KopcheekaApi.get_verification_token(response.id)
                self.session.headers.update({'Authorization': self.token})
                self.verify_email(verification_token)
        except Exception as e:
            Logger.error(f'{str(e)} | {self.token}')


def main():
    try:
        Discord().run()
    except Exception as e:
        Logger.error(e)

Logger.info('github.com/Pixens')
print()
with concurrent.futures.ThreadPoolExecutor(max_workers=__config__['threads']) as executor:
    for _ in open('./input/tokens.txt', 'r').read().splitlines():
        executor.submit(main)
