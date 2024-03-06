import logging
import os
import schedule
import time

from dotenv import load_dotenv
from mmpy_bot import Plugin

from utils import email_login, get_time_now, get_info_text, get_money_text, start_date, stop_date, split_text

from config import *


load_dotenv()
logger = logging.getLogger(__name__)

MAIN_CHANNEL_ID = os.getenv('MAIN_CHANNEL_ID')
START_JOB_TIME = START_JOB_HOUR + ':01'


def erase_log():
    """The log file is partially erased here"""
    try:
        list_file = []
        with open(LOG_FILE, 'r') as f:
            for count, line in enumerate(f):
                pass
            total_count = count
        if total_count > MAX_LINES_IN_LOG:
            with open(LOG_FILE, 'r') as f:
                for index, line in enumerate(f):
                    if index > (total_count - MAX_LINES_IN_LOG):
                        list_file.append(line)
        if list_file:
            with open(LOG_FILE, 'w') as f:
                f.writelines(list_file)
            logger.info(f'\nThe {LOG_FILE} file was partially cleaned. The last {MAX_LINES_IN_LOG} lines are saved.')
    except Exception:
        logger.warning(f'Unable to clear the {LOG_FILE} file.', exc_info=True)


class MMBotPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.imap = None

    def on_start(self):
        try:
            if not os.path.isfile('mail_uids.txt'):
                open('mail_uids.txt', 'w').close()
        except Exception as e:
            logger.exception('Creation error when launching the browsed emails file', exc_info=True)
            raise e
        if not MY_DEBUG:
            self.driver.create_post(channel_id=MAIN_CHANNEL_ID, message='Notification bot started!')
        self.run_scheduled()
        print(f'Notification bot runs!')

    def run_scheduled(self):
        """Setting scheduled tasks after the start of the bot"""
        schedule_in_start_day = schedule.every().second.do(self.run_main_job_once)
        main_schedule = schedule.every().day.at(START_JOB_TIME, JOB_TIME_ZONE).do(self.main_job)
        del_log = schedule.every().sunday.at(START_JOB_TIME, JOB_TIME_ZONE).do(erase_log)
        set_schedule = 'schedule_in_start_day, main_schedule, del_log'
        exec(set_schedule)

    def run_main_job_once(self):
        """Creating a task to run on the day of the bot run"""
        self.main_job()
        return schedule.CancelJob

    def send_message(self, text):
        self.driver.create_post(channel_id=MAIN_CHANNEL_ID, message=text)

    def main_job(self):
        """The main job with a loop of checking emails for the whole day
        and calculating the sum of income to the bank account at the end of the day"""
        jobs = schedule.get_jobs()
        logger.info(f'Scheduled tasks:\n    {jobs}')
        self.imap = email_login()
        current_time = get_time_now()
        start_time = start_date(START_JOB_HOUR).time()
        end_time = stop_date(STOP_JOB_HOUR).time()
        today = stop_date(STOP_JOB_HOUR).date().day
        logger.info(f'\n    Publication of information from the email has begun. Ends at {end_time} {JOB_TIME_ZONE}. '
                    f'Emails sent from {START_JOB_HOUR} to {STOP_JOB_HOUR} will be taken into review.')
        calculated: bool = False
        while (start_time <= current_time[0] <= end_time) and today == current_time[1]:
            time.sleep(TIMEOUT)
            if not self.imap:
                logger.info(f'The IMAP connection is broken.')
                self.imap = email_login()
            if not self.imap:
                continue
            text = get_info_text(self.imap)
            if text:
                if len(text) > MAX_COUNT_SIMBOL_INMESSAGE:
                    text_list = split_text(text, MAX_COUNT_SIMBOL_INMESSAGE)
                    for text in text_list:
                        self.send_message(text) if (not MY_DEBUG) else None
                    logger.debug(f'The message text is too large and was sent in parts')
                else:
                    self.send_message(text) if (not MY_DEBUG) else None
                    logger.debug(f'Notification has been sent:\n{text}')
            if (stop_date(STOP_CALCULATED_HOUR).time() <= current_time[0]) and not calculated:
                logger.info(f"\n    The calculation of the day's receipts has started."
                            f'Emails sent from {START_CALCULATED_HOUR} to {STOP_CALCULATED_HOUR} '
                            f'will be taken into review.')
                if not self.imap:
                    logger.info(f'The IMAP connection is broken.')
                    self.imap = email_login()
                if not self.imap:
                    continue
                text = get_money_text(self.imap)
                if text:
                    self.send_message(text) if (not MY_DEBUG) else None
                    logger.debug(f'Income count is done:\n    {text}')
                self.imap.close()
                calculated = True
            current_time = get_time_now()
        try:
            open('mail_uids.txt', 'w').close()
        except Exception:
            logger.warning('Unable to clear the browsed emails file.', exc_info=True)
        self.imap.logout()
        logger.info(f'\nSending of notices is completed today.')

