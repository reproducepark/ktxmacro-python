import os
import telegram
from dotenv import load_dotenv

class TelegramBot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramBot, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        load_dotenv()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = telegram.Bot(token=self.bot_token)
        self._initialized = True

    async def send_message(self, message):
        await self.bot.send_message(chat_id=self.chat_id, text=message) 