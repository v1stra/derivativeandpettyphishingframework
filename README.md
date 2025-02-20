# Phishing Framework

Phishing framework written in plain english so read the code to get a better understanding. This is just a reference.

Oh yeah and you need a landing page server, this doesn't do that just exposes an API for use in the landing page. Use like nginx or something.

This allows you more granularity with templates than GoPhish.

**This tool assumes you have already configured a SMTP Sending server. You should probably do this to pass SPF/DMARC checks. Digital Ocean has a great guide**

## Key Terms

- **Sending Server** - The SMTP server for which valid DNS records are already configured. Typically you would want a Postfix server with OpenDKIM and valid SPF, DMARC, and DKIM records so that you can bypass SPF and not sent to the spam folder
- **Landing Page** - This tool does not setup or configure a landing page for you in any way. It is actually designed to sit behind a landing page. The landing page being whatever the user sees when they click on your link. For example, a PHP landing page with Nginx as a reverse proxy would do well. Also you could use AWS S3/Cloudfront/Route53 for a static landing page. 
- **Template** - Jinja2 template that is rendered and used as the email template. The script checks the file extension for ".html" or ".txt" so make sure they are one of these types or they won't get attached. (It uses the file extension to determine MIME type of the message body).

## Installation
```
python3 -m venv .
source bin/activate
python3 -m pip install -r requirements.txt
python3 -m flask run
# or (check your opsec)
python3 -m flask run --host 0.0.0.0 
```

### Config
Configuration is set in `config.py`. Set this to change options.
```python
config = {
    "smtp": {
        "hostname": "localhost",
        "port": "25",
        "username": "",
        "password": ""
    },
    "throttle": {
        "seconds" : "2",
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
```

## Client Usage

Start the interactive shell
```
(dap) ubuntu@somehost:~/dap$ python3 client.py 
Initializing interactive shell...
```

### Help!
```
> help

Documented commands (type help <topic>):
========================================
adduser      exit      listoptions    loadusers   updatepayload
deletegroup  getgroup  listtemplates  sendemails
deleteuser   help      listusers      status 


> help adduser
 Adds a user to the database
        
        Usage:
            adduser -e email@example.com -f Test -l User -t "Tester of the emailz" -g test_group
            
        Args:
            The user's email:
                -e EMAIL, --email EMAIL
            The user's first name:
                -f FIRST, --first FIRST
            The user's last name:
                -l LAST, --last LAST
            The sending group name:
                -g GROUP, --group GROUP
            The user's organizational title:
                -t TITLE, --title TITLE


> help loadusers
 Load users from a csv file

        Usage:
            loadusers /path/to/users.csv
        
        Args:
            File path to CSV file containing users:
                
        Info:
            CSV file needs headers, an example:
                email,first_name,last_name,title,group_name
                travis@v1stra.io,Travis,Timmerman,Red Team Operator,group1


> help sendemails
 Sends emails to target group
        
        Usage:
            sendemails -g GROUP -t TEMPLATE -l LINK -s SENDER -S SUBJECT -e ENVELOPE_SENDER

        Args:
            Sending group name (string):
                -g GROUP, --group GROUP
            Template filename to send. Searches in /templates:
                -t TEMPLATE, --template TEMPLATE
            The link URL (e.g., https://example.com):
                -l LINK, --link LINK
            The sender, or "from" that the user sees:
                -s SENDER, --sender SENDER
            The subject of the email:
                -S SUBJECT, --subject SUBJECT
            The envelope sender. Should match sending domain to pass SPF:
                -e ENVELOPE_SENDER, --envelope_sender ENVELOPE_SENDER
```

Load users from a CSV
```
> loadusers example.csv
status: 200
"3 users loaded"
```
Format for loading CSV (if you mess this up it's sending it anyway :)):
```
email,first_name,last_name,title,group_name
travis@v1stra.io,Travis,Timmerman,Red Team Operator,group1
test-vhjpwcg5p@srv1.mail-tester.com,Mail,Tester,MAIL TESTER,group2
```

List users
```
> listusers
status: 200
email,first_name,group_name,id,last_name,title,unique_id
travis@v1stra.io,Travis,test_group,1,Timmerman,Red Team Operator,Isls3xuah6iGNxaC
test-vhjpwcg5p@srv1.mail-tester.com,Mail,test_group,3,Tester,MAIL TESTER,A8TWV5eAs2GSNgvc

```
Delete a user. Unique_id from previously added users
```
> deleteuser A8TWV5eAs2GSNgvc
status: 200
"ok"
```

Send emails. Jinja2 searches for templates in the *templates* folder by default.
```
> sendemails -g test_group --subject "[INTERNAL] File Transfer Service " --sender "File Transfer Service <test@exampledomain.net>" -L https://exampledomain.net/pickup.php -e test@exampledomain.net -t test.html
```

Templates go in the `templates` folder, list them like this:
```
> listtemplates
test.html
```

Add a user
``` 
> adduser -e "emusk@tesla.com" -f "Elon" -l "Musk" -t "CEO" -g spear_phish_targets 
status: 200
{"uid":"fr3NX9SASCUbx7Lt"}
```

List options/config
```
> listoptions
status: 200
{
 "db": {
  "sqlite": "sqlite:///dap.sqlite3"
 },
 "payload_file": {
  "file_name": "User Sees This Title.xls",
  "file_path": "payloads/payload.xls"
 },
 "smtp": {
  "hostname": "localhost",
  "password": "",
  "port": "25",
  "username": ""
 },
 "throttle": {
  "jitter": ".25",
  "seconds": "2"
 }
}
```

### Threads

The application threads out the sending process. This is useful for when a large group of users has been sent to. The `status` command can be used to see if the threads are still running.

```
> sendemails -g test_group -t file_pickup.html -s NoReplyTo@anydomain.com -S "File Pickup for You" -e test@mydomain.org -l https://test.example.com/pickup.php
status: 200
"thread 0 started"

> status
status: 200
[{"Thread 0":"Running"}]
```

### Logging

Various operations are logged to the server. Such as when a landing page sends a request to `/user/<UID>`. This will pull the email associated with that UID and log this to a file. The default location for these logs are the root of the application. For example:

```
ubuntu@testing:~/dap$ ll *.log
-rw-rw-r-- 1 ubuntu ubuntu   697 Feb  3 17:33 02-03-23.log
-rw-rw-r-- 1 ubuntu ubuntu 13855 Feb  7 15:33 02-06-23.log
-rw-rw-r-- 1 ubuntu ubuntu  1026 Feb  8 14:31 02-07-23.log
-rw-rw-r-- 1 ubuntu ubuntu  3410 Feb  9 15:44 02-08-23.log
-rw-rw-r-- 1 ubuntu ubuntu  4839 Feb 13 19:16 02-09-23.log
-rw-rw-r-- 1 ubuntu ubuntu  7645 Feb 13 22:15 02-13-23.log
-rw-rw-r-- 1 ubuntu ubuntu  2938 Feb 14 15:30 02-14-23.log

ubuntu@testing:~/dap$ tail 02-14-23.log]
```





