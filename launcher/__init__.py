import asyncio
import time
from utils import run_command, delay

class RobloxLauncher:
    def __init__(self, config):
        self.config = config
        self.package = "com.roblox.client"

    async def launch_instance(self, link):
        """Launch a single Roblox instance with the given link."""
        command = f'am start -a android.intent.action.VIEW -d "{link}"'
        success, output = run_command(command)
        return success

    async def launch_all(self):
        """Launch multiple instances with delay."""
        links = self.config.get('roblox_links', [])
        instances = self.config.get('instances', 1)
        delay_sec = self.config.get('delay', 1)

        for i in range(min(instances, len(links))):
            link = links[i % len(links)]  # Cycle through links if more instances than links
            if await self.launch_instance(link):
                if i < instances - 1:  # Don't delay after last
                    await asyncio.sleep(delay_sec)
            else:
                break  # Stop if launch fails

    async def stop_all(self):
        """Stop all Roblox processes."""
        command = f'am force-stop {self.package}'
        success, output = run_command(command)
        return success