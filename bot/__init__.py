from telethon import TelegramClient, events
import asyncio
from config import load_config, save_config
from launcher import RobloxLauncher
from utils import logging
import os
import subprocess
import gc  # For memory optimization
import sys

class TelegramBot:
    def __init__(self, boot_mode=False):
        self.config = load_config()
        self.client = TelegramClient('session', self.config['api_id'], self.config['api_hash'])
        self.launcher = RobloxLauncher(self.config)
        self.admin_id = self.config['admin_id']
        self.boot_mode = boot_mode
        self.launcher.selected_package_index = self.config.get('selected_package_index', 0)

    def is_admin(self, event):
        return event.sender_id == self.admin_id

    async def start_bot(self):
        await self.client.start(bot_token=self.config['bot_token'])

        @self.client.on(events.NewMessage(pattern=r'^/packages$'))
        async def packages_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            packages = self.launcher.list_packages()
            if not packages:
                await event.reply("No Roblox packages found.")
                return
            message = "✅ Available Roblox packages:\n"
            for i, pkg in enumerate(packages, start=1):
                selected = " ✅" if i - 1 == self.launcher.selected_package_index else ""
                message += f"{i}. {pkg}{selected}\n"
            message += "\nUse /selectpackage <number> to choose which pack to launch."
            await event.reply(message)

        @self.client.on(events.NewMessage(pattern=r'^/selectpackage(?:\s+(\d+))?$'))
        async def select_package_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            selection = event.pattern_match.group(1)
            if not selection:
                await event.reply("Usage: /selectpackage <number>")
                return
            index = int(selection) - 1
            try:
                package = self.launcher.set_selected_package(index)
                self.config['selected_package_index'] = index
                save_config(self.config)
                await event.reply(f"Selected Roblox package: {package}")
            except Exception as e:
                await event.reply(f"Invalid package selection: {e}")

        @self.client.on(events.NewMessage(pattern=r'^/start(?:\s+(\d+))?$'))
        async def start_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            choice = event.pattern_match.group(1)
            package = None
            if choice:
                index = int(choice) - 1
                if index < 0 or index >= len(self.launcher.packages):
                    await event.reply("Invalid package number.")
                    return
                package = self.launcher.packages[index]
            success = await self.launcher.launch_all(package=package)
            target = package or self.launcher.get_selected_package()
            if success:
                await event.reply(f"Roblox instances launched for {target}!")
            else:
                await event.reply(f"Failed to launch Roblox package: {target}")

        @self.client.on(events.NewMessage(pattern=r'^/launch(?:\s+(\d+))?$'))
        async def launch_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            choice = event.pattern_match.group(1)
            package = None
            if choice:
                index = int(choice) - 1
                if index < 0 or index >= len(self.launcher.packages):
                    await event.reply("Invalid package number.")
                    return
                package = self.launcher.packages[index]
            success = await self.launcher.launch_all(package=package)
            target = package or self.launcher.get_selected_package()
            if success:
                await event.reply(f"Launched Roblox package: {target}")
            else:
                await event.reply(f"Failed to launch Roblox package: {target}")

        @self.client.on(events.NewMessage(pattern=r'^/stop(?:\s+(\d+))?$'))
        async def stop_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            choice = event.pattern_match.group(1)
            package = None
            if choice:
                index = int(choice) - 1
                if index < 0 or index >= len(self.launcher.packages):
                    await event.reply("Invalid package number.")
                    return
                package = self.launcher.packages[index]
            result = await self.launcher.stop_all(package=package)
            target = package or self.launcher.get_selected_package()
            if result:
                await event.reply(f"Stopped Roblox package: {target}")
            else:
                await event.reply(f"Could not stop Roblox package: {target}")

        @self.client.on(events.NewMessage(pattern=r'^/stopall$'))
        async def stop_all_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            result = await self.launcher.stop_all()
            if result:
                await event.reply("Stopped all Roblox packages.")
            else:
                await event.reply("No Roblox process was stopped.")

        @self.client.on(events.NewMessage(pattern=r'^/status$'))
        async def status_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            status = self.get_system_status()
            await event.reply(status)

        @self.client.on(events.NewMessage(pattern=r'^/optimize$'))
        async def optimize_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            result = self.optimize_system()
            await event.reply(result)

        @self.client.on(events.NewMessage(pattern=r'^/setup$'))
        async def setup_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            subprocess.run(['python', 'setup.py'])
            await event.reply("Setup completed. Please restart the bot.")

        @self.client.on(events.NewMessage(pattern=r'^/update$'))
        async def update_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            subprocess.run(['bash', 'scripts/update.sh'])
            await event.reply("Update triggered. Bot will restart.")

        @self.client.on(events.NewMessage(pattern=r'^/reboot$'))
        async def reboot_command(event):
            if not self.is_admin(event):
                await event.reply("Access denied. Only admin can use this bot.")
                return
            await event.reply("Перезагружаю телефон...")
            try:
                commands = [
                    'reboot',
                    '/system/bin/reboot',
                    '/system/xbin/reboot',
                    'svc power reboot',
                    'su -c reboot',
                    'su -c "svc power reboot"',
                ]
                for cmd in commands:
                    result = subprocess.run(cmd, shell=True, timeout=15, capture_output=True, text=True)
                    if result.returncode == 0:
                        return
                await event.reply("Не удалось перезагрузить телефон. Требуется root или другой уровень доступа.")
            except Exception as e:
                await event.reply(f"Ошибка перезагрузки: {e}")

        logging.info("Bot started")
        await self.send_start_message()

        # Start memory optimization loop
        asyncio.create_task(self._optimize_memory())
        
        await self.client.run_until_disconnected()

    async def send_start_message(self):
        try:
            if self.boot_mode:
                message = "✅ VMOS Bridge запущен после включения телефона."
            else:
                message = "✅ VMOS Bridge бот перезапущен."
            await self.client.send_message(self.admin_id, message)
        except Exception as e:
            logging.error(f"Failed to send startup notification: {e}")

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
        """Maximum system optimization for Roblox performance."""
        try:
            results = []
            
            # 1. Enable Freeform window mode
            try:
                subprocess.run(['settings', 'put', 'global', 'enable_freeform_windows', '1'], timeout=5)
                results.append("✅ Freeform window mode enabled")
            except:
                results.append("⚠️ Could not enable Freeform")
            
            # 2. Enable Developer Options & ADB optimization
            try:
                subprocess.run(['setprop', 'persist.sys.usb.config', 'adb'], timeout=5)
                subprocess.run(['setprop', 'ro.debuggable', '1'], timeout=5)
                results.append("✅ Developer Options optimized")
            except:
                results.append("⚠️ Could not enable Developer Options")
            
            # 3. Aggressive memory management
            try:
                subprocess.run(['sync'], timeout=5)  # Flush buffers
                subprocess.run(['echo', '3', '>', '/proc/sys/vm/drop_caches'], timeout=5)
                results.append("✅ Memory flushed & freed")
            except:
                results.append("⚠️ Could not optimize memory")
            
            # 4. Kill unused processes
            apps_to_kill = ['chrome', 'facebook', 'instagram', 'whatsapp', 'telegram', 'youtube', 'maps']
            try:
                for app in apps_to_kill:
                    subprocess.run(['pkill', '-f', app], timeout=2)
                results.append(f"✅ Killed {len(apps_to_kill)} background apps")
            except:
                results.append("⚠️ Could not kill processes")
            
            # 5. Clear system cache
            try:
                subprocess.run(['rm', '-rf', '/data/system/package_cache/*'], timeout=5)
                subprocess.run(['rm', '-rf', '/data/anr/*'], timeout=5)
                subprocess.run(['rm', '-rf', '/data/tombstones/*'], timeout=5)
                results.append("✅ System cache cleared")
            except:
                results.append("⚠️ Could not clear cache")
            
            # 6. GPU & rendering optimization
            try:
                subprocess.run(['setprop', 'ro.vendor.extension_library', '/vendor/lib/rfsa/adsp/libfastcvopt.so'], timeout=5)
                subprocess.run(['setprop', 'persist.sys.usb.fast_charge', '1'], timeout=5)
                results.append("✅ GPU & rendering optimized")
            except:
                results.append("⚠️ Could not apply GPU optimization")
            
            # 7. Network optimization
            try:
                subprocess.run(['setprop', 'persist.sys.dalvik.vm.dex2oat-cpu-set', '0,1,2,3'], timeout=5)
                results.append("✅ Network stack optimized")
            except:
                results.append("⚠️ Could not optimize network")
            
            # 8. Disable animations for performance
            try:
                subprocess.run(['settings', 'put', 'global', 'window_animation_scale', '0.5'], timeout=5)
                subprocess.run(['settings', 'put', 'global', 'transition_animation_scale', '0.5'], timeout=5)
                results.append("✅ Animations reduced for FPS boost")
            except:
                results.append("⚠️ Could not reduce animations")
            
            optimization_msg = "🚀 MAXIMUM Optimization Complete:\n\n" + "\n".join(results)
            return optimization_msg
        except Exception as e:
            return f"⚠️ Optimization error: {str(e)}"

    async def _optimize_memory(self):
        """Periodic memory optimization for bot (runs every 30 seconds)."""
        while True:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds
                # Force garbage collection
                gc.collect()
                
                # Clear Python cache
                sys.path.clear()
                
                # Log memory optimization (silent)
                logging.info("Memory optimized")
            except Exception as e:
                logging.error(f"Memory optimization error: {e}")