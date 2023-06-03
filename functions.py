from discord_requests import *
import concurrent.futures, time

max_threads = config['threads']

def verify():
    tokens = open('input/tokens.txt', 'r').read().splitlines()
    s = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for i in range(len(tokens)):
                old_fulltoken = tokens[i]
                futures.append(executor.submit(claim, old_fulltoken))
    e = time.time()
                
    info(f'Threads finished. Time taken: {round(e-s, 3)}')    
    