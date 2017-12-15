import errno
from socket import error as socket_error

from flask import render_template
from flask_mail import Message
from .flask import APIException
from ..extentions import mail


def email_sender(recipients, subject, template, **kwargs):
    msg = Message()
    msg.subject = subject
    msg.html = render_template(template + '.html', **kwargs)
    msg.body = render_template(template + '.txt', **kwargs)

    try:
        if isinstance(recipients, list) and len(recipients) > 1:
            with mail.connect() as conn:
                for recipient in recipients:
                    msg.recipients = [recipient]
                    conn.send(msg)
        else:
            msg.recipients = [recipients]
            mail.send(msg)

    except socket_error as err:
        if err.errno is errno.ECONNREFUSED:
            raise APIException("Connection refused by the smtp server.", 500)
