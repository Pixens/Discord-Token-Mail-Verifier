import os
import threading
import ctypes
from concurrent.futures import ThreadPoolExecutor
from functions import *


if not config['kopcheeka_api_key']:
    error('Input your kopeechka API key in the config.')


resp = httpx.get(
    f"http://api.kopeechka.store/user-balance?token={config['kopcheeka_api_key']}&api=2.0")
if 'OK' not in resp.text:
    error('Error getting kopeechka balance: ' + resp.json()['value'])
    time.sleep(3)
    quit()

balance = resp.json()['balance']


def update_headers():
    while True:
        if os.name == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(
                f"https://discord.gg/boostup | https://github.com/Pixens/Token-Mail-Verifier | Verified: {data.verified} | Claimed: {data.claimed} | Balance: {balance} RUB")


# Concurrently verify tokens
with ThreadPoolExecutor(max_workers=5) as executor:
    executor.submit(verify)

    while True:
        update_headers()
