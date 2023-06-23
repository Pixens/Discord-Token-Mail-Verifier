import os
import secrets
import tempfile
from typing import List
import requests
import yaml

config = yaml.safe_load(open('config.yml', "r"))
api_key = config['kopcheeka_api_key']


def generate_password() -> str:
    return secrets.token_hex(16)


def remove(content_to_remove: List[str], file_path: str) -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        with open(file_path, 'r') as file:
            temp_file.writelines(line for line in file if not any(
                remove_content in line for remove_content in content_to_remove))
    os.replace(temp_file.name, file_path)


def write(line: str, filename: str) -> None:
    with open(filename, 'a') as f:
        f.write(f"{line}\n")


def get_mail() -> tuple[str, str]:
    mail_type = secrets.choice(config['email_domains'])
    url = f'https://api.kopeechka.store/mailbox-get-email?api=2.0&site=discord.com&sender=discord®ex=&mail_type={mail_type}&token={api_key}&soft=99'
    with requests.Session() as session:
        resp = session.get(url)
    if 'OK' in resp.text:
        return resp.json()['mail'], resp.json()['id']
    elif 'ERROR' in resp.text:
        if resp.json()['value'] == 'OUT_OF_STOCK':
            error('Email is out of stock! Saved as unclaimed.')
        if resp.json()['value'] == 'BAD_BALANCE':
            error('Not enough balance on kopeechka anymore! Saved as unclaimed.')
    return None, None


def cancel_mail(mail_id: str) -> None:
    url = f'https://api.kopeechka.store/mailbox-cancel?id={mail_id}&token={api_key}&api=2.0'
    with requests.Session() as session:
        session.get(url)


def get_code(mail_id: str) -> str:
    tries = 0
    while tries < 600:
        time.sleep(1)
        link = requests.get(
            f"http://api.kopeechka.store/mailbox-get-message?full=$FULL&id={mail_id}&token={api_key}&api=2.0").json()['value']
        if link != 'WAIT_LINK':
            cancel_mail(mail_id)
            link.replace('\\', '')
            break
        tries += 1
    else:
        cancel_mail(mail_id)
        return False
    verify_token = requests.get(link).url.split('#token=')[1]
    return verify_token
