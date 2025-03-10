
from json import JSONDecodeError
from csv import DictWriter
from io import StringIO

from json import loads

def json_to_csv(json: str):
    """ Converts JSON to CSV and returns it as a string """
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
