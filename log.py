import logging
from colorama import Fore, Style

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def info(content):
    if 'Verified' in content:
        level = '[v]'
    else:
        level = '[+]'
    message = f'{Fore.GREEN}{Style.BRIGHT}{level}{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
    logging.info(message)


def debug(content):
    message = f'{Fore.YELLOW}{Style.BRIGHT}[-]{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
    logging.debug(message)


def error(content):
    message = f'{Fore.RED}{Style.BRIGHT}[!]{Style.RESET_ALL} {Fore.RESET}{content}{Fore.RESET}'
    logging.error(message)
