import asyncio
from config import is_config_ready
from bot import TelegramBot
import os
import subprocess
import sys

def check_and_install_dependencies():
    """Check and install all required dependencies."""
    print("\n=== Checking dependencies... ===")
    
    try:
        import telethon
        print("✅ Telethon installed")
    except ImportError:
        print("❌ Telethon not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'telethon'], check=True)
        print("✅ Telethon installed")

def setup_autostart():
    """Setup Termux autostart if not already configured."""
    print("\n=== Setting up autostart ===")
    
    try:
        boot_dir = os.path.expanduser('~/.termux/boot')
        boot_script = os.path.join(boot_dir, 'start.sh')
        
        # Create boot directory
        os.makedirs(boot_dir, exist_ok=True)
        
        # Check if script already exists
        if os.path.exists(boot_script):
            print("✅ Autostart already configured")
            return
        
        # Get current project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create autostart script
        autostart_content = f'''#!/data/data/com.termux/files/usr/bin/bash

# VMOS Bridge Bot Autostart Script
cd "{project_dir}"
sleep 5
python main.py >> ~/vmosbridge.log 2>&1 &
exit 0
'''
        
        with open(boot_script, 'w') as f:
            f.write(autostart_content)
        
        # Make executable
        os.chmod(boot_script, 0o755)
        
        print(f"✅ Autostart configured: {boot_script}")
        print("📝 Note: Install 'Termux:Boot' app for automatic startup")
        
    except Exception as e:
        print(f"⚠️ Could not setup autostart: {e}")

if not is_config_ready():
    print("First run → starting setup...")
    subprocess.run([sys.executable, 'setup.py'])
    
print("Config loaded → checking environment...")

# Check dependencies
check_and_install_dependencies()

# Setup autostart
setup_autostart()

print("\n" + "="*50)
print("Starting bot...")
print("="*50 + "\n")

bot = TelegramBot()
asyncio.run(bot.start_bot())