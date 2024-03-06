import datetime
import email
import imaplib
import logging
import os
import pytz
import re
import unicodedata

from dotenv import load_dotenv
from email.header import decode_header

from config import *

load_dotenv()
logger = logging.getLogger(__name__)

SERVER = os.getenv('IMAP_SERVER')
NAME = os.getenv('EMAIL_NAME')
PASSWORD = os.getenv('EMAIL_PASSWORD')
PORT = int(os.getenv('IMAP_PORT'))

MSC = pytz.timezone(JOB_TIME_ZONE)

reg_1 = {'name': reg1_name, 'payment': reg1_payment, 'target': reg1_target}
reg_2 = {'name': reg2_name, 'payment': reg2_payment, 'target': reg2_target}


def get_time_now() -> list:
    """Getting the current time with using the time zone that is set in the settings file.
    And creating a time and a day without time zone from this date"""
    current_date = datetime.datetime.now(MSC)
    current_time = datetime.time(current_date.hour, current_date.minute, current_date.second)
    return [current_time, current_date.day]


def range_date() -> str:
    """Creating a string to search for email by date sent"""
    start_date = datetime.date.today()
    end_date = start_date + datetime.timedelta(days=1)
    if MY_DEBUG:
        start_date = start_date - datetime.timedelta(days=DELTA_DAYS)
    start_date_str = start_date.strftime('%d-%b-%Y')
    end_date_str = end_date.strftime('%d-%b-%Y')
    return f'(SINCE {start_date_str} BEFORE {end_date_str})'


def start_date(start_hour: str) -> datetime:
    """Getting the start date in the time zone, which is specified in the settings,
     using the specified hour in the bot settings."""
    c_d = datetime.datetime.now(MSC)
    start_time = datetime.datetime(c_d.year, c_d.month, c_d.day, int(start_hour), 0, 0)
    if MY_DEBUG:
        start_time = start_time - datetime.timedelta(days=DELTA_DAYS)
    return start_time


def stop_date(stop_hour: str) -> datetime:
    """Getting the stop date in the time zone, which is specified in the settings,
     using the specified hour in the bot settings."""
    c_d = datetime.datetime.now(MSC)
    return datetime.datetime(c_d.year, c_d.month, c_d.day, int(stop_hour) - 1, 59, 50)


def check_date(str_email_date: str, start_hour: str, end_hour: str) -> bool:
    """Converting the time of receiving email to the time zone that is set in the bot's settings.
     And checking that this time corresponds to the bot's operating time"""
    try:
        date = re.search(r'(.*\d\d\:\d\d\:\d\d.*\+\d{4})', str_email_date)[1]
    except Exception:
        date = re.search(r'(.*\d\d\:\d\d\:\d\d)', str_email_date)[1] + ' +0300'
    email_time = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
    email_time_job_tz = email_time.astimezone(pytz.timezone(JOB_TIME_ZONE))
    email_time_job_tz_naiv = datetime.time(email_time_job_tz.hour, email_time_job_tz.minute, email_time_job_tz.second)
    return (start_date(start_hour).time() < email_time_job_tz_naiv < stop_date(end_hour).time()) \
           and start_date(start_hour).date() <= email_time_job_tz.date()


def split_text(text: str, max_count_simbol_intext: int) -> list:
    """splitting text if it's too large to send in one message"""
    text_list = list()
    text_list.append(text)
    max_count_simbol_inpart = max_count_simbol_intext / 3
    count_simbol_inlines = round(len(text) / text.count('\n'))
    count_lines_inpart = round(max_count_simbol_inpart / count_simbol_inlines)
    while len(text_list[-1]) > max_count_simbol_inpart:
        text_1 = text_list.pop().replace('\n', '\r', count_lines_inpart)
        text_2 = text_1.replace('\r', '\n', count_lines_inpart - 1)
        pre_text_list = text_2.split('\r')
        text_list.extend(pre_text_list)
    return text_list


def pull_seen_mail_uids() -> set:
    """Reading from a file of email U_IDs that have already been viewed"""
    seen_mails = set()
    try:
        with open('mail_uids.txt', 'r') as f:
            while True:
                u_id = f.readline().strip()
                if not u_id:
                    break
                seen_mails.add(u_id)
    except Exception:
        open('mail_uids.txt', 'w').close()
        logger.warning(
            f'The notifications will be duplicated because the file of browsed email has been overwritten:\n',
            exc_info=True
        )
    logger.debug(f'U_id of previously viewed emails:\n{", ".join(map(str, seen_mails))}')
    return seen_mails


def push_seen_mail_uids(new_mails: set) -> None:
    """Record in a file the email U_IDs that have already been viewed"""
    with open('mail_uids.txt', 'a') as f:
        try:
            new_mails_str = ", ".join(map(str, new_mails))
            while True:
                f.writelines(str(new_mails.pop()) + '\n')
                if not new_mails:
                    break
        except Exception:
            logger.warning(f'Unable to replenish the browsed emails file:\n', exc_info=True)
        else:
            logger.debug(f'U_id of new emails viewed:\n{new_mails_str}')


def email_login() -> imaplib.IMAP4_SSL:
    """Creating a connection to an email"""
    try:
        imap = imaplib.IMAP4_SSL(SERVER, PORT)
    except Exception:
        logger.exception('Failed to create IMAP connection:', exc_info=True)
    else:
        try:
            imap.login(NAME, PASSWORD)
        except Exception:
            logger.exception('IMAP authentication error:', exc_info=True)
        else:
            logger.info(f'IMAP connection established')
            return imap


def search_info(content: str, regex: dict, email_date: str, email_from: str) -> dict:
    """Retrieve information from email content that meets search requirements"""
    name = regex['name']
    payment = regex['payment']
    target = regex['target']
    search_name = re.findall(name, content, re.IGNORECASE)[0]
    search_payment = re.findall(payment, content, re.IGNORECASE)[0]
    search_target = re.findall(target, content, re.IGNORECASE)[0]
    if ex_name.lower() not in search_name.lower():
        return {
            'email_date': email_date,
            'email_from': email_from,
            'name': search_name.strip(),
            'payment': search_payment.strip(),
            'target': search_target.strip(),
        }


def info_from_email(u_id: int, mail: list, start_hour: str, end_hour: str) -> dict:
    """Decode email and retrieve content from email that are received at the right time interval."""
    msg = email.message_from_bytes(mail[0][1])
    sender = decode_header(msg.get('From'))[-1][0]
    if isinstance(sender, bytes):
        sender = sender.decode()
    email_date = decode_header(msg.get('Date'))[0][0]
    try:
        email_from = re.search(r'\<(.*)\>', sender)[1]
    except TypeError:
        email_from = sender
    if email_from in email_from_list:
        check_email_date = check_date(email_date, start_hour, end_hour)
        logger.debug(f"Email detected: <{u_id}, date - {email_date} - {check_email_date}>")
        if check_email_date:
            for part in msg.walk():
                maintype = part.get_content_maintype()
                subtype = part.get_content_subtype()
                if maintype == 'text' and subtype == 'plain':
                    pre_content = None
                    try:
                        pre_content = part.get_payload(decode=True).decode()
                    except Exception:
                        logger.debug(f'On first try it is impossible to get content of email with u_id {u_id}'
                                     f' and date {email_date}')
                    if not pre_content:
                        try:
                            pre_content = part.get_payload(decode=True).decode('cp1251')
                        except Exception as e:
                            logger.warning(f'It is impossible to get content of email with u_id {u_id}'
                                           f' and date {email_date}:\n{e}')
                    if pre_content:
                        logger.debug(f'Got the contents of the email with u_id {u_id}')
                        content = unicodedata.normalize('NFKC', pre_content)
                        try:
                            info_1 = search_info(content, reg_1, email_date, email_from)
                        except Exception:
                            logger.debug(
                                f'Unable to parse email with u_id {u_id} and date {email_date} on pattern reg_1')
                        else:
                            if info_1:
                                return info_1
                        try:
                            info_2 = search_info(content, reg_2, email_date, email_from)
                        except Exception as e:
                            logger.warning(f'Unable to parse email with u_id {u_id} and date {email_date}:\n{e}')
                        else:
                            if info_2:
                                return info_2


def create_info_list(imap: imaplib.IMAP4_SSL) -> list:
    """Creation of the list with necessary information,
     only from those emails that were received in the specified time interval
     and have not been viewed yet"""
    start_hour = START_SEEN_HOUR
    end_hour = STOP_SEEN_HOUR
    imap.select('INBOX', readonly=True)
    result, data = imap.uid('search', range_date())
    u_ids = data[0]
    if u_ids:
        u_id_set = set((u_ids.decode('utf8')).split())
        new_mails = u_id_set.difference(pull_seen_mail_uids())
        if new_mails:
            info_list = list()
            for u_id in new_mails:
                result, mail = imap.uid('fetch', u_id, '(RFC822)')
                info = info_from_email(u_id, mail, start_hour, end_hour)
                if info:
                    info_list.append(info)
            push_seen_mail_uids(new_mails)
            if info_list:
                return info_list


def get_info_text(imap: imaplib.IMAP4_SSL) -> str:
    """Getting a text string with information from bank notifications to send inside the message"""
    info_list = create_info_list(imap)
    if info_list:
        info_text = str()
        for info in info_list:
            info_text = info_text + TEMPLATE_INF.format(
                f"{info['name']}",
                f"{info['payment']}",
                f"{info['target']}"
            ) + f'\n'
            logger.info(f"Information from the email dated {info['email_date']} was sent to the bot")
            logger.debug(f"Sender: <{info['email_from']}>, sum: <{info['payment']}>")
        return info_text


def create_money_list(imap: imaplib.IMAP4_SSL) -> list:
    """Creating a list with funds from email notifications of banks
    with setting the time interval for receiving these emails"""
    start_hour = START_CALCULATED_HOUR
    end_hour = STOP_CALCULATED_HOUR
    imap.select('INBOX', readonly=True)
    result, data = imap.uid('search', range_date())
    u_ids = data[0].split()
    if u_ids:
        money_list = list()
        for u_id in u_ids:
            result, mail = imap.uid('fetch', u_id, '(RFC822)')
            info = info_from_email(u_id, mail, start_hour, end_hour)
            if info:
                money_list.append(info['payment'])
        if money_list:
            return money_list


def get_money_text(imap: imaplib.IMAP4_SSL) -> str:
    """Getting a text string with the sum of receipts from bank notifications,
    which was received on the account, to send inside the message"""
    moneys = create_money_list(imap)
    if moneys:
        money_text = TEMPLATE_MON.format(f"{calculate_sum(moneys)}")
        return money_text


def calculate_sum(moneys: list) -> float:
    """Calculation of the sum of receipts that came into the bank account"""
    sum: float = 0
    for s in moneys:
        s1 = s.replace(",", ".")
        s2 = s1.replace(" ", "")
        s3 = re.search('((\d+)[.]?(\d*))', s2)[0]
        sum += float(s3)
    return round(sum, 2)


if __name__ == '__main__':

    if MY_DEBUG:
        imap = email_login()
        open('mail_uids.txt', 'w').close()
        print(get_info_text(imap))
        print(get_money_text(imap))
