import yaml
import httpx
import random
import time
import threading
import os
import re

from kopeechka import KopeechkaApiError, MailActivations
from colorama import Fore, Style


os.system("")
__config__ = yaml.safe_load(open('config.yml', 'r').read())


class KopeechkaApi:
    def __init__(self):
        self.api_key = __config__['kopcheeka_api_key']
        self.api = MailActivations(api_token=self.api_key)
    
    def get_email(self):
        try:
            response = self.api.mailbox_get_email(site='discord.com', mail_type=random.choice(__config__['email_domains']), soft_id=99)
            if response.status == 'OK':
                return response
            else:
                raise Exception('Failed to get email.')
        except KopeechkaApiError as e:
            raise Exception(e)

    def get_token_by_link(self, link: str):
        return str(httpx.get(link, follow_redirects=True).url).split('https://discord.com/verify#token=')[1]
        
    def get_verification_token(self, task_id):
        tries = 0
        while tries < 300:
            response = httpx.get(f"http://api.kopeechka.store/mailbox-get-message?id={task_id}&token={self.api_key}&api=2.0")
            if 'OK' in response.text:
                token = self.get_token_by_link(response.json()['value'])
                return token
            else:
                tries += 1
                time.sleep(1)
                
        self.api.mailbox_cancel(task_id)     
        raise Exception('Mail not received.')


class Utils:
    @staticmethod
    def remove(content, filename):
        lock = threading.Lock()
        with lock:
            with open(filename, 'r') as file:
                lines = file.readlines()
            lines = [line for line in lines if content not in line]
            with open(filename, 'w') as file:
                file.writelines(lines)
    
    @staticmethod
    def write(content, filename):
        file_lock = threading.Lock()
        with file_lock:
            with open(filename, 'a') as file:
                file.write(f'{content}\n')
    
    @staticmethod
    def get_build_number():
        #Taken from https://github.com/Sysys242/
        res = httpx.get("https://discord.com/login").text 
        file_with_build_num = 'https://discord.com/assets/' + \
        re.compile(r'assets/+([a-z0-9]+)\.js').findall(res)[-2]+'.js'
        req_file_build = httpx.get(file_with_build_num).text
        index_of_build_num = req_file_build.find('buildNumber')+24
        return int(req_file_build[index_of_build_num:index_of_build_num+6])


class Logger:
    @staticmethod
    def info(content):
        message = f'{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
        print(message)

    @staticmethod
    def error(content):
        message = f'{Fore.RED}{Style.BRIGHT}[!]{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
        print(message)
