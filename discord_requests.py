import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from client import generate_session
from utils import generate_password, get_mail, get_code, cancel_mail, remove, write

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class data:
    claimed = 0
    verified = 0


def claim(old_fulltoken):
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(1, 4):
            token = old_fulltoken.split(':')[-1]
            if ':' in old_fulltoken:
                password = old_fulltoken.split(':')[1]
            else:
                password = generate_password()
            mail, mail_id = get_mail()
            if mail is None:
                return
            try:
                payload = {
                    'email': mail,
                    'password': password
                }
                with generate_session(token) as session:
                    resp = session.patch(
                        'https://discord.com/api/v9/users/@me', json=payload)
                    if resp.status_code == 200:
                        new_fulltoken = f"{mail}:{password}:{resp.json()['token']}"
                        logging.info(f'Claimed token | {token}')
                        data.claimed += 1
                        executor.submit(verify_token, session,
                                        old_fulltoken, new_fulltoken, mail_id)
                        remove(old_fulltoken, 'input/tokens.txt')
                        write(new_fulltoken, 'output/claimed.txt')
                        return
                    else:
                        logging.debug(f'Failed to claim token | {token}')
                        cancel_mail(mail_id)
                        return
            except Exception as e:
                logging.error(e)
    logging.debug(f'Failed to claim token | {token}')
    cancel_mail(mail_id)
    return


def verify_token(session, old_fulltoken, new_fulltoken, mail_id):
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i, _ in enumerate(range(1, 4)):
            token = new_fulltoken.split(':')[-1]
            mail = new_fulltoken.split(':')[0]
            password = new_fulltoken.split(':')[1]
            session.headers['authorization'] = token
            session.headers['referer'] = 'https://discord.com/verify'
            verify_token = get_code(mail_id)
            if verify_token is False:
                logging.debug(f'Failed to get verification code | {token}')
                write(fulltoken, 'output/unverified.txt')
                remove(old_fulltoken, 'input/tokens.txt')
                return
            try:
                payload = {
                    'captcha_key': None,
                    'token': verify_token
                }
                resp = session.post(
                    'https://discord.com/api/v9/auth/verify', json=payload)
                if resp.status_code == 200:
                    verified_token = resp.json()['token']
                    verified_fulltoken = f'{mail}:{password}:{verified_token}'
                    logging.info(f'Verified mail | {verified_token}')
                    data.verified += 1
                    write(verified_fulltoken, 'output/verified.txt')
                    return
                else:
                    logging.debug(f'Failed to verify mail | {token}')
                    write(verified_fulltoken, 'output/unverified.txt')
                    return
            except Exception as e:
                logging.error(e)
    logging.debug(f'Failed to verify mail | {token}')
    write(new_fulltoken, 'output/unverified.txt')
    return


if __name__ == '__main__':
    old_fulltoken = 'example_token'
    claim(old_fulltoken)
