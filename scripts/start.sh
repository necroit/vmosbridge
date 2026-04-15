#!/data/data/com.termux/files/usr/bin/bash

# Termux boot script - copy to ~/.termux/boot/start.sh
# This script runs automatically when Termux starts

# LOG FILE
LOG_FILE="$HOME/vmosbridge_startup.log"

echo "[$(date)] Starting VMOS Bridge Bot..." >> "$LOG_FILE"

# Change to project directory (update path if needed)
# Common paths in Termux/VMOS:
# - /data/data/com.termux/files/home/vmosbridge
# - /sdcard/vmosbridge
# - /storage/emulated/0/vmosbridge

cd /data/data/com.termux/files/home/vmosbridge || cd /storage/emulated/0/vmosbridge || cd ~/vmosbridge || {
    echo "[$(date)] ERROR: Could not find vmosbridge directory" >> "$LOG_FILE"
    exit 1
}

echo "[$(date)] Changed to $(pwd)" >> "$LOG_FILE"

# Wait for system to fully boot
sleep 3

# Run system optimization first
echo "[$(date)] Running system optimization..." >> "$LOG_FILE"
python main.py --optimize >> "$LOG_FILE" 2>&1 &

# Wait a bit before starting bot
sleep 5

# Start bot in background
echo "[$(date)] Starting bot..." >> "$LOG_FILE"
python main.py --boot >> "$LOG_FILE" 2>&1 &

echo "[$(date)] Bot started (PID: $!)" >> "$LOG_FILE"
exit 0