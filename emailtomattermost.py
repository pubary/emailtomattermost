import importlib
import os

from dotenv import load_dotenv
from mmpy_bot import Bot, Settings

from plugin import MMBotPlugin

importlib.import_module('log_config')
load_dotenv()

bot = Bot(
    settings=Settings(
        MATTERMOST_URL=os.getenv('MATTERMOST_URL'),
        MATTERMOST_PORT=int(os.getenv('MATTERMOST_PORT')),
        MATTERMOST_API_PATH='/api/v4',
        BOT_TOKEN=os.getenv('MM_BOT_TOKEN'),
        BOT_TEAM=os.getenv('MM_BOT_TEAM'),
        SSL_VERIFY=False,
    ),
    plugins=[MMBotPlugin()],
)

bot.run()
