# configuration options go here

config = {
    "smtp": {
        "hostname": "localhost",
        "port": "25",
        "username": "",
        "password": ""
    },
    "throttle": {
        "batch_size": "20",
        "seconds" : "5",
        "jitter": ".25"
    },
    "db": {
        "sqlite": "sqlite:///dap.sqlite3"
    },
    "payload_file": {
        "file_name": "Filename As Seen By Victim.xls",
        "file_path": "payloads/path-to-file-on-disk.xls",
    },
}