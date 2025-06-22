#!/bin/bash

# Set paths
LOCAL_DIR="/home/thala/videos"
NAS_DIR="/mnt/File_share"
LOCK_FILE="/tmp/upload_videos.lock"
LOG_FILE="/home/thala/upload_log.txt"

# Prevent multiple instances of the script running simultaneously
if [ -f "$LOCK_FILE" ]; then
    echo "$(date) - Another instance is running. Exiting..." | tee -a "$LOG_FILE"
    exit 1
fi
touch "$LOCK_FILE"

# Ensure the Videos folder exists
mkdir -p "$LOCAL_DIR"

# Check if NAS is mounted
if ! mount | grep -q "$NAS_DIR"; then
    echo "$(date) - ERROR: NAS not mounted at $NAS_DIR. Skipping upload." | tee -a "$LOG_FILE"
    rm -f "$LOCK_FILE"
    exit 1
fi

# Check internet connectivity
if ! ping -c 2 8.8.8.8 > /dev/null 2>&1; then
    echo "$(date) - No internet. Will retry later..." | tee -a "$LOG_FILE"
    rm -f "$LOCK_FILE"
    exit 1
fi

echo "$(date) - Internet and NAS available, syncing videos..." | tee -a "$LOG_FILE"

# Find files that haven't changed in the last 2 minutes (to avoid uploading active files)
find "$LOCAL_DIR" -type f -mmin +2 | while read -r file; do
    if [ ! -f "$file" ]; then
        continue  # Skip if the file was already removed
    fi

    echo "$(date) - Uploading $file..." | tee -a "$LOG_FILE"

    # Perform rsync and preserve file if it fails
    rsync -av --ignore-existing --no-perms --no-owner --no-group --omit-dir-times --remove-source-files "$file" "$NAS_DIR"

    if [ $? -eq 0 ]; then
        echo "$(date) - Successfully uploaded $file" | tee -a "$LOG_FILE"
    else
        echo "$(date) - ERROR: Failed to upload $file. Keeping it for next attempt." | tee -a "$LOG_FILE"
    fi
done

# Cleanup: Delete empty directories inside videos folder
find "$LOCAL_DIR" -mindepth 1 -type d -empty -delete

echo "$(date) - Sync complete!" | tee -a "$LOG_FILE"

# Remove the lock file after execution
rm -f "$LOCK_FILE"

sleep 60
