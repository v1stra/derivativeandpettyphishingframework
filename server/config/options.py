# server configuration options go here

Options = {
    "smtp": {
        "hostname": "mail.mail-relay.it.com",
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
    "threads" : 1
}