import asyncio
import subprocess
import time
from utils import run_command, delay

class RobloxLauncher:
    def __init__(self, config):
        self.config = config
        self.packages = self.find_roblox_packages()

    def find_roblox_packages(self):
        """Find all Roblox-related packages on device."""
        try:
            result = subprocess.run(['pm', 'list', 'packages'], capture_output=True, text=True)
            packages = [line.split(':')[1] for line in result.stdout.split('\n') if 'roblox' in line.lower()]
            return packages
        except Exception:
            return ['com.roblox.client']  # Fallback

    def select_package(self):
        """Return the currently selected Roblox package."""
        selected = self.get_selected_package()
        if selected:
            return selected
        return 'com.roblox.client'

    def get_selected_package(self):
        if not self.packages:
            return None
        if getattr(self, 'selected_package_index', None) is None or self.selected_package_index >= len(self.packages):
            self.selected_package_index = 0
        return self.packages[self.selected_package_index]

    def set_selected_package(self, index):
        if not self.packages:
            raise ValueError("No Roblox packages available")
        if index < 0 or index >= len(self.packages):
            raise ValueError("Invalid package index")
        self.selected_package_index = index
        return self.packages[index]

    def list_packages(self):
        return self.packages

    async def launch_instance(self, link, package):
        """Launch a single Roblox instance with the given link."""
        commands = [
            f'am start -a android.intent.action.VIEW -d "{link}" -p "{package}" -f 0x10200000',
            f'am start -a android.intent.action.VIEW -d "{link}" -p "{package}" -f 0x18000000',
            f'am start -a android.intent.action.VIEW -d "{link}" -p "{package}"',
        ]
        for command in commands:
            success, output = run_command(command)
            if success:
                return True
        return False

    def check_and_enable_freeform(self):
        """Check if Freeform is enabled, if not - enable it."""
        enabled = False
        try:
            result = subprocess.run(['settings', 'get', 'global', 'enable_freeform_windows'],
                                    capture_output=True, text=True, timeout=5)
            if 'null' in result.stdout or '0' in result.stdout:
                subprocess.run(['settings', 'put', 'global', 'enable_freeform_windows', '1'], timeout=5)
                enabled = True
        except Exception:
            pass

        try:
            subprocess.run(['settings', 'put', 'global', 'enable_freeform_support', '1'], timeout=5)
        except Exception:
            pass

        try:
            subprocess.run(['settings', 'put', 'global', 'force_resizable_activities', '1'], timeout=5)
        except Exception:
            pass

        return enabled

    async def launch_all(self, package=None, instances=None, delay_sec=None):
        """Launch configured Roblox instances for a selected package."""
        self.check_and_enable_freeform()
        package = package or self.select_package()
        if not package:
            return False

        links = self.config.get('roblox_links', [])
        instances = instances if instances is not None else self.config.get('instances', 1)
        delay_sec = delay_sec if delay_sec is not None else self.config.get('delay', 1)

        launched = 0
        for i in range(min(instances, len(links))):
            link = links[i % len(links)]
            if await self.launch_instance(link, package):
                launched += 1
                if i < instances - 1:
                    await asyncio.sleep(delay_sec)
            else:
                break

        return launched > 0

    async def stop_all(self, package=None):
        """Stop Roblox processes for one or all packages."""
        targets = [package] if package else self.packages
        if not targets:
            targets = ['com.roblox.client']
        
        stopped_any = False
        for target in targets:
            methods = [
                f'pkill -f {target}',
                f'killall {target.split('.')[-1]}',
            ]
            for cmd in methods:
                try:
                    result = subprocess.run(cmd, shell=True, timeout=5, capture_output=True)
                    stderr = result.stderr.decode('utf-8', errors='ignore') if isinstance(result.stderr, bytes) else str(result.stderr)
                    if result.returncode == 0 or 'No such process' not in stderr:
                        stopped_any = True
                        break
                except Exception:
                    continue
        return stopped_any