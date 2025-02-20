import smtplib

from time import sleep
from threading import Thread, Lock
from queue import Queue
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .utils import *

class Email:
    def __init__(self, body, recipient_email, message_sender, envelope_sender, subject, link_value, mime_type):
        self.body = body
        self.recipient_email = recipient_email
        self.message_sender = message_sender
        self.envelope_sender = envelope_sender
        self.subject = subject
        self.link_value = link_value
        self.mime_type = mime_type

    def send(self):

        resp = ''

        try:
            # connect to SMTP server
            server = smtplib.SMTP(SMTPSERVER)  # this code assumes you have a postfix server running locally
            
            resp += f"Connected to SMTP server {SMTPSERVER}\n"
            
            # perform SMTP EHLO
            resp += f"Sending server EHLO\n"

            server.ehlo()

            email_message = MIMEMultipart()
            email_message['From'] = self.message_sender
            email_message['To'] = self.recipient_email
            email_message['Subject'] = self.subject
            email_message['List-Unsubscribe'] = f'<mailto:{self.envelope_sender}?subject=unsubscribe>'

            email_message.attach(MIMEText(self.body, self.mime_type))

            message = email_message.as_string()

            # set envelope sender (pass SPF)
            server.mail(f"<{self.envelope_sender}>\n")

            # set recipient
            server.rcpt(self.recipient_email)

            resp += f'Sending email to "{self.recipient_email}" - "{self.subject}"\n'
            
            # set the message data
            server.data(message)

            # done
            resp += f"Sending completed.\n"
            server.quit()
            
        except (ConnectionRefusedError, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPResponseException, smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused) as e:
            resp += f"An SMTP error occured: {e}"

        return resp


class Sender:
    threads = []
    def __init__(self, n_threads, sleep_time, jitter):
        self.n_threads = n_threads
        self.sleep_time = sleep_time
        self.jitter = float(jitter)
        self.queue = Queue()
        self.log_file_lock = Lock()

    def enqueue(self, body, recipient_email, message_sender, envelope_sender, subject, link_value, mime_type):
        self.queue.put(Email(body, recipient_email, message_sender, envelope_sender, subject, link_value, mime_type))

    def worker(self):

        while True:
            email = self.queue.get()
            resp = email.send()

            with self.log_file_lock:
                log_write(resp)

            sleep(generate_throttle(self.sleep_time, self.jitter))
            
            self.queue.task_done()

    def run(self):
        for n in range(self.n_threads):
            thread = Thread(target=self.worker, daemon=True)
            self.threads.append(thread)
            thread.start()


