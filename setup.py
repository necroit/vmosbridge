from config import load_config, save_config
import subprocess
import sys
import os

def ask(msg):
    return input(msg + ": ").strip()

def check_dependencies():
    """Check and install dependencies."""
    print("\n=== Checking dependencies ===")
    
    try:
        import telethon
        print("✅ Telethon installed")
    except ImportError:
        print("❌ Telethon not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'telethon'], check=True)
        print("✅ Telethon installed")

def setup_termux_autostart():
    """Setup Termux autostart script."""
    try:
        boot_dir = os.path.expanduser('~/.termux/boot')
        boot_script = os.path.join(boot_dir, 'start.sh')
        
        os.makedirs(boot_dir, exist_ok=True)
        
        if not os.path.exists(boot_script):
            project_dir = os.path.dirname(os.path.abspath(__file__))
            
            autostart_content = f'''#!/data/data/com.termux/files/usr/bin/bash

# VMOS Bridge Bot Autostart
cd "{project_dir}"
sleep 5
python main.py --boot >> ~/vmosbridge.log 2>&1 &
exit 0
'''
            
            with open(boot_script, 'w') as f:
                f.write(autostart_content)
            
            os.chmod(boot_script, 0o755)
            
            print("\n✅ Autostart configured")
            print("📝 Install 'Termux:Boot' app for automatic startup\n")
    except Exception as e:
        print(f"\n⚠️ Could not setup autostart: {e}\n")

def main():
    # Check dependencies first
    check_dependencies()
    
    print("\n=== FIRST SETUP ===\n")
    print("Get API credentials from https://my.telegram.org/")
    print("Get Bot Token from @BotFather\n")

    cfg = load_config()

    if 'api_id' not in cfg:
        cfg["api_id"] = int(ask("Enter API ID (from my.telegram.org)"))
    if 'api_hash' not in cfg:
        cfg["api_hash"] = ask("Enter API Hash (from my.telegram.org)")
    if 'bot_token' not in cfg:
        cfg["bot_token"] = ask("Enter Bot Token (from @BotFather)")
    if 'admin_id' not in cfg:
        cfg["admin_id"] = int(ask("Enter your Telegram User ID (admin)"))

    if 'instances' not in cfg:
        cfg["instances"] = int(ask("How many Roblox instances"))
    if 'delay' not in cfg:
        cfg["delay"] = int(ask("Delay between launches (sec)"))

    if 'roblox_links' not in cfg:
        links = ask("Roblox links (comma separated)").split(",")
        cfg["roblox_links"] = [x.strip() for x in links if x.strip()]

    save_config(cfg)

    print("\nDONE. Config saved.\n")
    
    # Optional: Setup autostart (user can do it manually)
    print("\n=== Optional: Autostart Setup ===")
    setup_autostart = input("Setup autostart for Termux? (Y/N): ").strip().lower()
    if setup_autostart == 'y':
        setup_termux_autostart()
    else:
        print("⏭️  Skipped. You can manually set it up later.")

if __name__ == "__main__":
    main()