import string
import secrets

def generate_random_ascii(length: int):
    """ Generates a random ASCII string of specified length """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

