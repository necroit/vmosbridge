#!/data/data/com.termux/files/usr/bin/bash

# Termux boot script: copy this to ~/.termux/boot/start.sh
cd /path/to/your/project  # Replace with actual path in Termux

# Run update
bash scripts/update.sh

# Start bot in background
python main.py &