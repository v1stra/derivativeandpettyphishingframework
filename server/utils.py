import secrets
import string
import os

from datetime import datetime
from json import loads, JSONDecodeError
from csv import DictWriter
from io import StringIO
from hashlib import sha256
from random import uniform

from .config import Config

LOGFILE = f'{datetime.now().strftime("%m-%d-%y")}.log'
SMTPSERVER = f'{Config["smtp"]["hostname"]}:{Config["smtp"]["port"]}'
THROTTLE_SECONDS = int(Config['throttle']['seconds'])

def get_payload_hash_sha256():
    """ gets the sha265 hexdigest from the payload specified in config

    Returns:
        string: upper-case hex digest 
    """
    try:
        with open(Config["payload_file"]["file_path"], "rb") as f:
            file_bytes = f.read()

            return sha256(file_bytes).hexdigest().upper()
    except FileNotFoundError as ex:
        return sha256(b'').hexdigest().upper()

def get_payload_file_size():
    try:
        return os.path.getsize(Config["payload_file"]["file_path"])
    except FileNotFoundError as ex:
        return 0

def generate_random_string(length):
    """ Generates a random ASCII string of specified length

    Args:
        length (integer): length

    Returns:
        string: random ASCII string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


def log_write(data):
    """ Logs to the file specified by utils.LOGFILE with prepended date

    Args:
        data (string): text to be logged
    """
    with open(LOGFILE, 'a') as f:
        f.write(f'[{datetime.now()}] - {data}\n')


def json_to_csv(json):
    """ Converts JSON to CSV and returns it as a string

    Args:
        json (string): Json string
    """
    try:
        data = loads(json)
        output = StringIO()
        if len(data) > 0:
            writer = DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            for user in data:
                writer.writerow(user)
            return output.getvalue()

    except JSONDecodeError as e:
        return "Error decoding json"


def generate_throttle(seconds: int, jitter: float) -> float:
    """ Generates a floating point representation of sleep time with jitter """
    low = seconds - (seconds * jitter)
    high = seconds + (seconds * jitter)
    return uniform(low, high)