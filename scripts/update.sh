#!/bin/bash

echo "Checking for updates..."

# Fetch latest
git fetch origin

# Get current commit
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Updates found. Pulling..."
    git reset --hard origin/main
    git pull origin main
    echo "Update complete. Restarting bot..."
    # Kill current bot if running
    pkill -f "python main.py"
    # Restart
    python main.py &
else
    echo "No updates found."
fi