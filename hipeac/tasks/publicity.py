import email
import imaplib
import json
import lxml.html
import os
import re

from celery.decorators import periodic_task
from celery.schedules import crontab
from email.header import decode_header, make_header
from email.utils import parseaddr, parsedate_to_datetime
from lxml.html.clean import Cleaner

from hipeac.models import Profile, PublicityEmail
from hipeac.tools.language import NaturalLanguageAnalyzer


MAX_SPAM_LEVEL = 2
PUBLICITY_BOT_PASSWORD = os.environ.get('PUBLICITY_BOT_PASSWORD')


def decode_string(string: str) -> str:
    return str(make_header(decode_header(string)))


def parse_address(address: str):
    return parseaddr(decode_string(address))


def process_sympa_msg(msg_subject: str, content: str):
    try:
        if 'signoff list hipeac.publicity' in msg_subject:
            email = msg_subject.split(' ')[-1]
            Profile.objects.filter(user__email__iexact=email).update(is_subscribed=False)
        if 'hipeac.publicity automatic bounce management' in msg_subject:
            emails = [line for line in content.splitlines() if parseaddr(line) is not ('', '') and '@' in line]
            Profile.objects.filter(user__email__in=emails).update(is_bouncing=True)
        return True
    except Exception:
        return False


@periodic_task(run_every=crontab(minute='*/20'), max_retries=3)
def sync_emails():
    """Connects with email server and syncs emails sent to `publicity@hipeac.net`."""
    mbox = imaplib.IMAP4_SSL('mail.gandi.net')
    mbox.login('publicity.bot@hipeac.net', PUBLICITY_BOT_PASSWORD)
    mbox.select(mailbox='INBOX')

    res, data = mbox.search(None, 'ALL')

    for num in data[0].split():
        res, data = mbox.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        msg_subject = ' '.join(decode_string(msg['Subject']).split())
        addresses = {
            'from': [parse_address(address) for address in msg.get_all('from', [])],
            'to': [parse_address(address) for address in msg.get_all('to', [])],
        }
        spam_level = len(msg['X-Spam-Level']) if msg['X-Spam-Level'] else 0

        if spam_level > MAX_SPAM_LEVEL:
            mbox.store(num, '+FLAGS', '\\Deleted')
            continue

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() not in ['text/plain', 'text/html']:
                    continue  # check attachments
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                if content_type == 'text/plain':
                    break
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)

        content = str(payload, 'utf8', 'replace')

        if addresses['from'][0] == ('SYMPA', 'listserv@lists.ugent.be'):
            if process_sympa_msg(msg_subject, content):
                mbox.store(num, '+FLAGS', '\\Deleted')
            continue

        if content_type == 'text/html':
            cleaner = Cleaner()
            cleaner.javascript = True
            cleaner.style = True
            html = lxml.html.fromstring(content)
            content = cleaner.clean_html(html).text_content()

        try:
            PublicityEmail.objects.create(
                msgid=msg['Message-ID'],
                date=parsedate_to_datetime(msg['Date']),
                subject=msg_subject,
                content=re.sub(r'\n\s*\n', '\n\n', content).strip(),
                content_type=content_type,
                from_addresses=json.dumps(addresses['from']),
                to_addresses=json.dumps(addresses['to']),
                spam_level=spam_level,
                keywords=json.dumps(NaturalLanguageAnalyzer().get_keywords(content, min_salience=0.01)),
            )
            mbox.store(num, '+FLAGS', '\\Deleted')
        except Exception:
            continue

    mbox.expunge()
    mbox.close()
    mbox.logout()
