import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    """Run a shell command and return success."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"Command executed: {command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}, error: {e.stderr}")
        return False, e.stderr

def delay(seconds):
    """Sleep for seconds."""
    import time
    time.sleep(seconds)