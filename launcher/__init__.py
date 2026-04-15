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
        """Let user select Roblox package if multiple found."""
        if len(self.packages) == 1:
            return self.packages[0]
        elif len(self.packages) > 1:
            print("\n=== Found multiple Roblox packages ===")
            for i, pkg in enumerate(self.packages):
                print(f"{i+1}. {pkg}")
            while True:
                try:
                    choice = int(input("Select package number: ")) - 1
                    if 0 <= choice < len(self.packages):
                        return self.packages[choice]
                except ValueError:
                    pass
                print("Invalid choice. Try again.")
        else:
            print("No Roblox packages found. Using default.")
            return 'com.roblox.client'

    async def launch_instance(self, link, package):
        """Launch a single Roblox instance with the given link in Freeform window."""
        # Launch with Freeform window flags
        command = f'am start -a android.intent.action.VIEW -d "{link}" --windowingMode 2 --display-windowed --task-on-home'
        success, output = run_command(command)
        return success

    def check_and_enable_freeform(self):
        """Check if Freeform is enabled, if not - enable it."""
        try:
            # Check if Freeform is enabled
            result = subprocess.run(['settings', 'get', 'global', 'enable_freeform_windows'], 
                                  capture_output=True, text=True, timeout=5)
            if 'null' in result.stdout or '0' in result.stdout:
                # Enable Freeform
                subprocess.run(['settings', 'put', 'global', 'enable_freeform_windows', '1'], timeout=5)
                return True  # Was disabled, now enabled
            return False  # Already enabled
        except Exception:
            return None  # Error

    async def launch_all(self):
        """Launch multiple instances with delay in Freeform window."""
        # Check and enable Freeform mode
        freeform_status = self.check_and_enable_freeform()
        
        package = self.select_package()
        links = self.config.get('roblox_links', [])
        instances = self.config.get('instances', 1)
        delay_sec = self.config.get('delay', 1)

        for i in range(min(instances, len(links))):
            link = links[i % len(links)]  # Cycle through links if more instances than links
            if await self.launch_instance(link, package):
                if i < instances - 1:  # Don't delay after last
                    await asyncio.sleep(delay_sec)
            else:
                break  # Stop if launch fails

    async def stop_all(self, package=None):
        """Stop all Roblox processes."""
        if not package:
            package = self.select_package()
        
        # Try multiple methods to stop the app
        methods = [
            f'pkill -f {package}',  # Method 1: pkill by package name
            f"killall {package.split('.') [-1]}",  # Method 2: killall by app name
        ]
        
        for cmd in methods:
            try:
                result = subprocess.run(cmd, shell=True, timeout=5, capture_output=True)
                if result.returncode == 0 or 'No such process' not in result.stderr:
                    return True
            except Exception:
                continue
        
        return False