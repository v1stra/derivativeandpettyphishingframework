# configuration options go here

Config = {
    "smtp": {
        "hostname": "localhost",
        "port": "25",
        "username": "",
        "password": ""
    },
    "throttle": {
        "seconds" : 1,
        "jitter": ".25"
    },
    "db": {
        "sqlite": "sqlite:///dap.sqlite3"
    },
    "payload_file": {
        "file_name": "Filename As Seen By Victim.xls",
        "file_path": "payloads/path-to-file-on-disk.xls",
    },
    "threads" : 1
}