
from datetime import datetime

LOGFILE = f'{datetime.now().strftime("%m-%d-%y")}.log'

def log_write(data: str):
    """ Logs to the file specified by utils.LOGFILE with prepended date """
    with open(LOGFILE, 'a') as f:
        f.write(log_format(data))

def log_format(data: str) -> str:
    """ Generates a log-formatted string """
    return f"[{datetime.now()}] - {data}\n"