from config import load_config, save_config

def ask(msg):
    return input(msg + ": ").strip()

def main():
    print("\n=== FIRST SETUP ===\n")

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

if __name__ == "__main__":
    main()