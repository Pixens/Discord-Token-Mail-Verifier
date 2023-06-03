from client import *
from utils import *

class data:
    claimed = 0; verified = 0

def claim(old_fulltoken):
    for i in range(1,4):
        
        token = old_fulltoken.split(':')[-1]
        if ':' in old_fulltoken:
            password = old_fulltoken.split(':')[1]
        else:
            password = generate_password()
            
        mail, mail_id = get_mail()
        if mail == None:
            return
        
        try:
            payload = {
                'email': mail,
                'password': password
            }
            session = generate_session(token)
            resp = session.patch('https://discord.com/api/v9/users/@me', json = payload)
            if resp.status_code == 200:
                new_fulltoken = f"{mail}:{password}:{resp.json()['token']}"
                info(f'Claimed token | {token}')
                data.claimed += 1
                remove(old_fulltoken, 'input/tokens.txt')
                write(new_fulltoken, 'output/claimed.txt')
                return verify_token(session, old_fulltoken, new_fulltoken, mail_id)
            else:
                debug(f'Failed to claim token | {token}')
                cancel_mail(mail_id)
                return
            
        except Exception as e: 
            print(e)
        
    debug(f'Failed to claim token | {token}')
    cancel_mail(mail_id)
    return
    
    
def verify_token(session, old_fulltoken, new_fulltoken, mail_id):
    for i in range(1,4):
        token = new_fulltoken.split(':')[-1]
        mail = new_fulltoken.split(':')[0]
        password = new_fulltoken.split(':')[1]
        session.headers['authorization'] = token
        session.headers['referer'] = 'https://discord.com/verify'
        verify_token = get_code(mail_id)
        if verify_token == False:
            debug(f'Failed to get verification code | {token}')
            write(fulltoken, 'output/unverified.txt')
            remove(old_fulltoken, 'input/tokens.txt')
            return
        try:
            payload = {
                'captcha_key': None, 
                'token': verify_token
            }
            
            resp = session.post('https://discord.com/api/v9/auth/verify', json = payload)
            if resp.status_code == 200:
                verified_token = resp.json()['token']
                verified_fulltoken = f'{mail}:{password}:{verified_token}'
                info(f'Verified mail | {verified_token}')
                data.verified += 1
                write(verified_fulltoken, 'output/verified.txt')
                return
            else:
                debug(f'Failed to verify mail | {token}')
                write(verified_fulltoken, 'output/unverified.txt')
                return
            
        except Exception as e: 
            continue
    
    debug(f'Failed to verify mail | {token}')
    write(new_fulltoken, 'output/unverified.txt')
    return
