MY_DEBUG = False
JOB_TIME_ZONE = 'Europe/Moscow'
TIMEOUT: int = 35  # break between email checks (on default = 35)

START_JOB_HOUR: str = '00'  # the hour when chat messages start to be sent (on default = '00')
if MY_DEBUG:
    STOP_JOB_HOUR: str = '24'  # finish hour for seen emails and calculated sum (min='01',max='24')
    DELTA_DAYS: int = 0  # possible additional past days for seen emails and calculated sum
else:
    STOP_JOB_HOUR: str = '24'  # the hour when chat messaging stops (on default = '24')

START_SEEN_HOUR: str = START_JOB_HOUR  # emails received after this hour will be reviewed for send messages to the chat
STOP_SEEN_HOUR: str = STOP_JOB_HOUR  # emails received after this hour will not be reviewed for send messages to chat
START_CALCULATED_HOUR: str = START_JOB_HOUR  # start hour for calculated sum
STOP_CALCULATED_HOUR: str = '19'  # stop hour for calculated sum (min='01', max='24')


TEMPLATE_INF: str = 'Пришла оплата от **{}** на сумму **{}** Назначение платежа: {}'
TEMPLATE_MON: str = 'За день на РС поступило **{}** руб.'

email_from_list: list = ['first@e.mail', 'second@e.mail']  # list of addresses from which banks send notifications


reg1_name: str = r'ООО "МОЯ КОМПАНИЯ": от (.+) на счёт '
reg1_payment: str = r'на счёт \d+ зачислена сумма (.+)[\n\r]*'
reg1_target: str = r'Остаток: \d+[.]?\d*.+ [.\n\r]*(.+)'
reg2_name: str = r'Контрагент: (.+)'
reg2_payment: str = r'Сумма операции: (.+)'
reg2_target: str = r'Назначение платежа: (.+)'
ex_name: str = 'Моя Компания'

MAX_COUNT_SIMBOL_INMESSAGE: int = 16380  # Mattermost setting
LOG_FILE = 'emailtomattermost.log'  # name of the .log file
MAX_LINES_IN_LOG = 500  # number of undeleted lines in the log file after it was partially cleared
