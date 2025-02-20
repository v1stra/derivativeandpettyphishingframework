import requests
import sys
import cmd
import urllib3
import shlex
import argparse

from os import listdir
from server.config import Config
from server.utils import json_to_csv
from json import dumps
from csv import DictReader


class Shell(cmd.Cmd):
    
    def __init__(self):
        super().__init__()
        self.prompt = '> '
        self.interactive = False
        self.proxies = {
            # 'http': 'http://127.0.0.1:8080'
        }

        self.target = 'http://127.0.0.1:5000'
        
        
    def send_request(self, uri, method, json={}):
        """ wrapper around requests library methods

        Args:
            uri (string): the URI of the API (ex. "/emails/send")
            method (string): "GET" or "POST" only
            json (dict, optional): dict to be converted to json. Defaults to {}.

        Returns:
            requests.response: complete response object
        """
        if method == 'POST':
            resp = requests.post(f'{self.target}{uri}', json=json, proxies=self.proxies, verify=False)
        elif method == 'GET':
            resp = requests.get(f'{self.target}{uri}', proxies=self.proxies, verify=False)
            
        return resp, resp.status_code
    
    
    def listusers(self, group=None):
        """ Lists users in the database. Optionally passing a group.

        Args:
            group (string, optional): Group name. Defaults to None.
        """
        if group:
            resp, sc = self.send_request(f'/groups/{group}', 'GET')
        else:
            resp, sc = self.send_request('/users', 'GET')
            
        print(json_to_csv(resp.text))

        
    def adduser(self, email, first, last, group, title=None):
        """ adds a user to the database

        Args:
            email (string): email
            first (string): first name
            last (string): last name
            group (string): group name
            title (string, optional): person's title. Defaults to None.
        """
        data = {
            'email': email,
            'first_name': first,
            'last_name': last,
            'group_name': group,
            'title': title
        }
        resp, sc = self.send_request('/users/add', 'POST', json=data)
        print(resp.text)
        
        
    def deleteuser(self, uid):
        """ Delete a user by uid

        Args:
            uid (string): uid value generated for the user
        """
        resp, sc = self.send_request(f'/user/{uid}/delete', 'GET')
        
        print(resp.text)
    
    
    def sendemails(self, group, template, link, sender, subject, envelope_sender):
        """ sends emails in batch to user groups
        
        Args:
            group (string): group name of user groups
            template (string): template file name in templates director (ex. test.html)
            link (string): link to the landing page (ex. https://example.com/landing.php)
            sender (string): sender of the email (user sees)
            subject (string): subject of the email
            envelope_sender (string): the sender in the envelope (transparent - match sending dom)
        """
        data = {
            'pretext_template': template,
            'group_name': group,
            'link_value': link,
            'sender': sender,
            'subject': subject,
            'envelope_sender': envelope_sender
        }
        
        resp, sc = self.send_request('/emails/send', 'POST', json=data)
        
        print(resp.text)
    
    
    def loadusers(self, target_file):
        """ load users from a CSV file

        Args:
            target_file (string): path to csv file containing users
        """
        try:
            with open(target_file, 'r') as csv_file:
                reader = DictReader(csv_file)
                user_list = []
                for row in reader:
                    user_list.append(row)
                resp = self.send_request('/users/load', 'POST', json=user_list)
                print(resp.text)
                        
        except FileNotFoundError as e:
            print(f'File {target_file} not found.')
        
    
    def listtemplates(self):
        """ list templates within template path
        """
        for template in listdir("server/templates"):
            print(template)
        
        
    def testemail(self):
        data = {
            'pretext_template': 'test_email.html',
            'sender': 'Do Not Reply <donotreply@exampledomain.net>',
            'subject': 'DAP Test Email',
            'envelope_sender':  'test@exampledomain.net'
        }


    def listoptions(self):
        
        resp = self.send_request('/config', 'GET')

        print(dumps(resp.json(), indent=1))

        
    def updatepayload(self, file_path):
        """ Updates the payload with a POST request to the server """

        data = {
            'file_path': file_path
        }

        resp, sc = self.send_request('/config/payload', 'POST', json=data)

        print(resp.text)

    
    def getgroup(self, group):
        """ Gets all members of a group and returns CSV """
        
        resp, sc = self.send_request(f'/groups/{group}', 'GET')

        print(json_to_csv(resp.text))

    def deletegroup(self, group):
        """ Deletes all users identified by a group name """
        resp, sc = self.send_request(f'/groups/{group}/delete', 'GET')
        print(resp.text)

    def status(self):
        resp, sc = self.send_request('/emails/status', 'GET')
        print(resp.text)

    def listgroups(self):
        resp, sc = self.send_request('/groups', 'GET')
        if sc == 200:
            print(dumps(resp.json(), indent=1))
        else:
            print(f"invalid status: {sc}")

    def getuser(self, uid):
        resp, sc = self.send_request(f'/user/{uid}', 'GET')
        if sc == 200:
            print(dumps(resp.json(), indent=1))
        else:
            print(f"invalid status: {sc}")

    def findusers(self, searchval):
        resp, sc = self.send_request(f'/search/user/{searchval}', 'GET')
        if sc == 200:
            print(dumps(resp.json(), indent=1))
        else:
            print(f"invalid status: {sc}")

    ##########################################
    #### Registered Command Functions ########

    def emptyline(self):
        """ Do nothing when empty line is input """
        pass

    def do_listusers(self, line):
        """ Lists users in the database """

        args = shlex.split(line)

        self.listusers(args[0] if len(args) else None)
        

    def do_loadusers(self, line):
        """ Load users from a csv file

        Usage:
            loadusers /path/to/users.csv
        
        Args:
            File path to CSV file containing users:
                
        Info:
            CSV file needs headers, an example:
                email,first_name,last_name,title,group_name
                travis@v1stra.io,Travis,Timmerman,Red Team Operator,group1
        """

        args = shlex.split(line)

        self.loadusers(args[0]) if len(args) else print('Argument required: file')
        
    
    def do_sendemails(self, line):
        """ Sends emails to target group
        
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
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            exit_on_error=False
            )
            
        parser.add_argument('-g', '--group')
        parser.add_argument('-t', '--template')
        parser.add_argument('-l', '--link')
        parser.add_argument('-s', '--sender')
        parser.add_argument('-S', '--subject')
        parser.add_argument('-e', '--envelope_sender')
        
        args = parser.parse_args(shlex.split(line))
        if not all([args.group, args.template, args.link, args.sender, args.subject, args.envelope_sender]):
            print('Incorrect number of arguments')
        else:
            self.sendemails(args.group, args.template, args.link, args.sender, args.subject, args.envelope_sender)
    

    def do_adduser(self, line):
        """ Adds a user to the database
        
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
        """
        parser = argparse.ArgumentParser(
            add_help=False,
            exit_on_error=False
            )

        parser.add_argument('-e', '--email')
        parser.add_argument('-f', '--first')
        parser.add_argument('-l', '--last')
        parser.add_argument('-g', '--group')
        parser.add_argument('-t', '--title')
        
        args = parser.parse_args(shlex.split(line))
        if not all([args.email, args.first, args.last, args.group]):
            print('Not enough arguments')
        else:
            self.adduser(args.email, args.first, args.last, args.group, args.title)

    
    def do_deleteuser(self, line):
        """ Delete a user from the database
        
        Usage:
            deleteuser UID
            
        Args:
            Unique identifier generated when a user is added:
        """
        args = shlex.split(line)

        self.deleteuser(args[0]) if len(args) else print('User\'s unique_id (uid) required')

    
    def do_listtemplates(self, line):
        """ List templates in the /templates folder """
        self.listtemplates()

    def do_updatepayload(self, line):
        """ Updates the payload with a file on disk (must be accessible on server)

        Usage:
            updatepayload path/to/file.txt

        Args:
            File path that should be present on server:
        """
        args = shlex.split(line)

        self.updatepayload(args[0]) if len(args) else print('Argument required: file')


    def do_getgroup(self, line):
        """ Lists users in a group

        Usage:
            getgroup GROUP

        Args:
            Name of the user group
        """

        args = shlex.split(line)

        self.getgroup(args[0]) if len(args) else print('group name required')


    def do_deletegroup(self, line):
        """ Deletes all users in a group

        Usage:
            deletegroup GROUP

        Args:
            Name of the user group
        """

        args = shlex.split(line)

        self.deletegroup(args[0]) if len(args) else print('group name required')


    def do_status(self, line):
        """ Returns the status of sending threads """
        self.status()

    def do_exit(self, line):
        """ Exits the prompt """
        return True

    def do_listoptions(self, line):
        """ Lists options from the server """
        self.listoptions()

    def do_listgroups(self, line):
        """ List groups on the server """
        self.listgroups()

    def do_getuser(self, line):
        """ Gets user info 
        
        Usage:
            getuser UID

        Args:
            Unique ID of the user
        """
        args = shlex.split(line)
        self.getuser(args[0]) if len(args) else print('user uid required')

    def do_findusers(self, line):
        """ Find users by email

        Args:
            Email (or partial email) of the user
        """
        args = shlex.split(line)
        self.findusers(args[0]) if len(args) else print('search value required')

    def interactive_prompt(self, intro='Initializing interactive shell...'):
        """ Start the interactive command prompt """
        self.interactive = True
        do_quit = False
        while do_quit is not True:
            try:
                self.cmdloop(intro=intro)
                do_quit = True
            except KeyboardInterrupt:
                sys.stdout.write('\n')
        self.interactive = False


def main():
    
    urllib3.disable_warnings()

    repl = Shell()
    repl.interactive_prompt()


if __name__ == '__main__':
    main()
