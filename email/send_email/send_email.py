#!/usr/bin/env python3


import smtplib
import os.path as op
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders


def send_mail(send_from, send_to, subject, message, files=[], server="127.0.0.1", port=25, timeout=5, use_auth=False, username='', password='', use_starttls=False, use_tls=False):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list): to name - a bare string will be treated as a list with 1 address
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        use_auth (bool): use username and password to login smtpd server
        username (str): server auth username
        password (str): server auth password
        use_starttls (bool): use STARTTLS mode
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message + '\n'))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(op.basename(path)))
        msg.attach(part)

    if use_tls:
        smtp_tls = smtplib.SMTP_SSL(server, port, timeout=timeout)
        if use_auth:
            smtp_tls.login(username, password)
        smtp_tls.sendmail(send_from, send_to, msg.as_string())
        smtp_tls.quit()
    else:
        smtp = smtplib.SMTP(server, port, timeout=timeout)
        if use_starttls:
            smtp.starttls()
        if use_auth:
            smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.quit()

#send_mail('manak@secar.cz', 'rama@secar.cz', 'subject text', 'message text', files=['/etc/hosts'], server="192.168.221.207", port='25', use_auth=False, username='', password='', use_starttls=True)
send_mail('rrastik@seznam.cz', 'rama@secar.cz', 'subject text', 'message text', files=['/etc/hosts'], server="smtp.seznam.cz", port='465', use_auth=True, username='rrastik@seznam.cz', password='mypassword', use_tls=True)
