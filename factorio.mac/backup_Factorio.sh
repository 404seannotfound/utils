#!/bin/bash

# Define the Factorio save folder and backup location
FACTORIO_SAVE_DIR="$HOME/Library/Application Support/factorio/saves"
BACKUP_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Games/Factorio"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Find the latest save game file
LATEST_SAVE=$(ls -t "$FACTORIO_SAVE_DIR"/*.zip 2>/dev/null | head -n 1)

# Check if a save game file exists
if [ -z "$LATEST_SAVE" ]; then
    echo "No save files found in $FACTORIO_SAVE_DIR."
    exit 1
fi

# Get the base name of the latest save file
SAVE_BASENAME=$(basename "$LATEST_SAVE")

# Define the duplicate save file path
DUPLICATE_SAVE="$BACKUP_DIR/backup_$(date +%Y%m%d%H%M%S)_$SAVE_BASENAME"

# Copy the latest save game file to the backup location
cp "$LATEST_SAVE" "$DUPLICATE_SAVE"

# Verify the operation
if [ $? -eq 0 ]; then
    echo "Successfully backed up $SAVE_BASENAME to $DUPLICATE_SAVE."
else
    echo "Failed to back up $SAVE_BASENAME."
    exit 1
fi

