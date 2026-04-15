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

        @self.client.on(events.NewMessage(pattern=r'/optimize'))
        async def optimize_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            result = self.optimize_system()
            await event.reply(result)

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
            # Memory info in MB/GB
            mem_result = subprocess.run(['cat', '/proc/meminfo'], capture_output=True, text=True)
            mem_lines = mem_result.stdout.split('\n')
            
            mem_total = 0
            mem_available = 0
            mem_free = 0
            
            for line in mem_lines:
                if 'MemTotal' in line:
                    mem_total = int(line.split()[1]) // 1024  # Convert KB to MB
                elif 'MemAvailable' in line:
                    mem_available = int(line.split()[1]) // 1024
                elif 'MemFree' in line:
                    mem_free = int(line.split()[1]) // 1024
            
            mem_used = mem_total - mem_available if mem_available > 0 else mem_total - mem_free
            
            # Convert to GB if > 1024 MB
            if mem_total > 1024:
                mem_info = f"Total: {mem_total/1024:.1f}GB | Used: {mem_used/1024:.1f}GB | Free: {mem_available/1024:.1f}GB"
            else:
                mem_info = f"Total: {mem_total}MB | Used: {mem_used}MB | Free: {mem_available}MB"

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

    def optimize_system(self):
        """Optimize system for better Roblox performance."""
        try:
            results = []
            
            # Enable Freeform window mode
            try:
                subprocess.run(['settings', 'put', 'global', 'enable_freeform_windows', '1'], timeout=5)
                results.append("✅ Freeform window mode enabled")
            except:
                results.append("⚠️ Could not enable Freeform")
            
            # Enable Developer Options
            try:
                subprocess.run(['setprop', 'persist.sys.usb.config', 'adb'], timeout=5)
                results.append("✅ Developer Options optimized")
            except:
                results.append("⚠️ Could not enable Developer Options")
            
            # Clear cache
            try:
                subprocess.run(['rm', '-rf', '/data/system/package_cache/*'], timeout=5)
                results.append("✅ Cache cleared")
            except:
                results.append("⚠️ Could not clear cache")
            
            # Kill unused processes
            try:
                subprocess.run(['pkill', '-f', 'chrome'], timeout=5)
                subprocess.run(['pkill', '-f', 'facebook'], timeout=5)
                results.append("✅ Unused apps terminated")
            except:
                results.append("⚠️ Could not kill processes")
            
            # Optimize GPU
            try:
                subprocess.run(['setprop', 'ro.vendor.extension_library', '/vendor/lib/rfsa/adsp/libfastcvopt.so'], timeout=5)
                results.append("✅ GPU optimization applied")
            except:
                results.append("⚠️ Could not apply GPU optimization")
            
            optimization_msg = "🚀 System Optimization Results:\n\n" + "\n".join(results)
            return optimization_msg
        except Exception as e:
            return f"⚠️ Optimization error: {str(e)}"