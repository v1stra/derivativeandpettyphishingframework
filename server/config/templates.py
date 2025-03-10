from datetime import datetime

from ..utils import generate_random_ascii

# Define variables that can be added to the template here
template_variables = {
    "file_name": "File Name.pdf",
    "file_description": "Generic File Description",
    "date_now_1": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "date_now_2": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
    "random_value_16": generate_random_ascii(16),
    "random_value_5": generate_random_ascii(5),
    "not_real_var": "it's real now"
}