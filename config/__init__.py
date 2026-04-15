import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # If file exists but is empty or invalid, return empty dict
        return {}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

def is_config_ready():
    config = load_config()
    required = ['api_id', 'api_hash', 'bot_token', 'admin_id', 'roblox_links', 'instances', 'delay']
    return all(key in config and config[key] for key in required)