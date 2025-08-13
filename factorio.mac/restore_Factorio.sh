#!/bin/bash

# Define the Factorio save folder and backup location
FACTORIO_SAVE_DIR="$HOME/Library/Application Support/factorio/saves"
BACKUP_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Games/Factorio"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Find the latest backup file
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.zip 2>/dev/null | head -n 1)

# Check if a backup file exists
if [ -z "$LATEST_BACKUP" ]; then
    echo "No backup files found in $BACKUP_DIR."
    exit 1
fi

# Get the base name of the latest backup file
BACKUP_BASENAME=$(basename "$LATEST_BACKUP")

# Define the restore save file path
RESTORE_SAVE="$FACTORIO_SAVE_DIR/$BACKUP_BASENAME"

# Copy the latest backup file to the Factorio save folder
cp "$LATEST_BACKUP" "$RESTORE_SAVE"

# Verify the operation
if [ $? -eq 0 ]; then
    echo "Successfully restored $BACKUP_BASENAME to $RESTORE_SAVE."
else
    echo "Failed to restore $BACKUP_BASENAME."
    exit 1
fi
