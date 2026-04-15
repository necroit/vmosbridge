import asyncio
from config import is_config_ready
from bot import TelegramBot
import os
import subprocess

if not is_config_ready():
    print("First run → starting setup...")
    subprocess.run(['python', 'setup.py'])
    exit()

print("Config loaded → starting bot...")

bot = TelegramBot()
asyncio.run(bot.start_bot())