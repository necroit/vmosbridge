from telethon import TelegramClient, events
import asyncio
from config import load_config
from launcher import RobloxLauncher
from utils import logging
import os
import subprocess

class TelegramBot:
    def __init__(self):
        self.config = load_config()
        self.client = TelegramClient('session', self.config['api_id'], self.config['api_hash'])
        self.launcher = RobloxLauncher(self.config)
        self.admin_id = self.config['admin_id']

    def is_admin(self, event):
        return event.sender_id == self.admin_id

    async def start_bot(self):
        await self.client.start(bot_token=self.config['bot_token'])

        @self.client.on(events.NewMessage(pattern=r'/start'))
        async def start_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            await self.launcher.launch_all()
            await event.reply("Roblox instances launched!")

        @self.client.on(events.NewMessage(pattern=r'/stop'))
        async def stop_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            await self.launcher.stop_all()
            await event.reply("Roblox stopped!")

        @self.client.on(events.NewMessage(pattern=r'/status'))
        async def status_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            status = self.get_system_status()
            await event.reply(status)

        @self.client.on(events.NewMessage(pattern=r'/screenshot'))
        async def screenshot_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            screenshot_path = self.take_screenshot()
            if screenshot_path:
                await self.client.send_file(event.chat_id, screenshot_path, caption="Screenshot")
            else:
                await event.reply("Failed to take screenshot")

        @self.client.on(events.NewMessage(pattern=r'/setup'))
        async def setup_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            # Run setup in subprocess
            subprocess.run(['python', 'setup.py'])
            await event.reply("Setup completed. Please restart the bot.")

        @self.client.on(events.NewMessage(pattern=r'/update'))
        async def update_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            # Run update script
            subprocess.run(['bash', 'scripts/update.sh'])
            await event.reply("Update triggered. Bot will restart.")

        logging.info("Bot started")
        await self.client.run_until_disconnected()

    def get_system_status(self):
        """Get system status: memory, running processes, etc."""
        try:
            # Memory info
            mem_result = subprocess.run(['cat', '/proc/meminfo'], capture_output=True, text=True)
            mem_lines = mem_result.stdout.split('\n')[:3]  # First 3 lines
            mem_info = '\n'.join(mem_lines)

            # Roblox processes - check all found packages
            roblox_processes = []
            for pkg in self.launcher.packages:
                ps_result = subprocess.run(['ps'], capture_output=True, text=True)
                pkg_processes = [line for line in ps_result.stdout.split('\n') if pkg in line.lower()]
                roblox_processes.extend(pkg_processes)

            roblox_count = len(roblox_processes)

            status = f"🖥️ System Status:\n\n📊 Memory:\n{mem_info}\n\n🎮 Roblox Processes: {roblox_count} running"
            return status
        except Exception as e:
            return f"Error getting status: {str(e)}"

    def take_screenshot(self):
        """Take screenshot and return path."""
        try:
            screenshot_path = "/sdcard/screenshot.png"
            subprocess.run(['screencap', '-p', screenshot_path], check=True)
            return screenshot_path
        except subprocess.CalledProcessError:
            return None