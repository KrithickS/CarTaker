#!/usr/bin/env python3
import os
import subprocess
import time
from datetime import datetime

# Define video folder
video_folder = "/home/thala/Videos"
os.makedirs(video_folder, exist_ok=True)

# Generate timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
video_file = f"{video_folder}/surveillance_{timestamp}.mp4"

# Command to record video
record_command = [
    "libcamera-vid", "-t", "0", "--width", "1920", "--height", "1080",
    "--framerate", "30", "--bitrate", "5000000", "--codec", "libav",
    "-o", video_file
]

# Start recording
print(f"Recording started: {video_file}")
process = subprocess.Popen(record_command)

# Run indefinitely
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping recording...")
    process.terminate()
