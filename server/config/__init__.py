from datetime import datetime

from .options import Options
from .templates import template_variables

SMTPSERVER = f'{Options["smtp"]["hostname"]}:{Options["smtp"]["port"]}'
THROTTLE_SECONDS = int(Options['throttle']['seconds'])

