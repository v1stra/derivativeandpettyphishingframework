import string
import os

from hashlib import sha256

def get_file_sha256(file_path: string):
    """ gets the sha265 hexdigest of the bytes loaded by file_path """
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()

            return sha256(file_bytes).hexdigest().upper()
    except FileNotFoundError as ex:
        return sha256(b'').hexdigest().upper()


def get_file_size(file_path: string):
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError as ex:
        return 0
    
    