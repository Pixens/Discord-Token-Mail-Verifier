from colorama import Fore, Style
import os

os.system("")


def info(content):
    if 'Verified' in content:
        level = '[v]'
    else:
        level = '[+]'
    message = f'{Fore.GREEN}{Style.BRIGHT}{level}{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
    print(message)
    
def debug(content):
    message = f'{Fore.YELLOW}{Style.BRIGHT}[-]{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
    print(message)
    
def error(content):
    message = f'{Fore.RED}{Style.BRIGHT}[!]{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
    print(message)