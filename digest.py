import email
import imaplib
import re

from email.header import decode_header, make_header
from email.utils import parseaddr


MAX_SPAM_LEVEL = 3


def decode_string(string: str) -> str:
    return str(make_header(decode_header(string)))


def parse_address(address: str):
    return parseaddr(decode_string(address))


def process_sympa_msg(msg_subject: str, content: str):
    if 'signoff list hipeac.publicity' in msg_subject:
        print(msg_subject.split(' ')[-1])
    if 'hipeac.publicity automatic bounce management' in msg_subject:
        emails = [line for line in content.splitlines() if parseaddr(line) is not ('', '') and '@' in line]
        print(emails)

    return False


def sync_emails():
    """Connects with email server and syncs emails sent to `publicity@hipeac.net`."""
    # https://docs.python.org/3/library/email.message.html#email.message.EmailMessage
    mbox = imaplib.IMAP4_SSL('mail.gandi.net')
    mbox.login('publicity.bot@hipeac.net', 'X+otfdyi(z)4]k#4DTC%P,GXu-<V#~nWo6sNb{m]')
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

        content = re.sub(r'\n\s*\n', '\n\n', str(payload, 'utf8', 'replace')).strip()

        if addresses['from'][0] == ('SYMPA', 'listserv@lists.ugent.be'):
            if process_sympa_msg(msg_subject, content):
                mbox.store(num, '+FLAGS', '\\Deleted')
            continue

    mbox.expunge()
    mbox.close()
    mbox.logout()


sync_emails()
