from discord_requests import *
import concurrent.futures
import time

max_threads = config['threads']


def verify():
    tokens = open('input/tokens.txt', 'r').read().splitlines()
    s = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(claim, old_fulltoken)
                                   : old_fulltoken for old_fulltoken in tokens}
        for future in concurrent.futures.as_completed(futures):
            old_fulltoken = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                error(f'Token {old_fulltoken} generated an exception: {exc}')
            else:
                info(f'Token {old_fulltoken} verified successfully')
    e = time.time()

    info(f'Threads finished. Time taken: {round(e-s, 3)}s')
