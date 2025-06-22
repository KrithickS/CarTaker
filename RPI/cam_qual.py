from picamera2 import Picamera2
import time

# (Optional) print all detected cameras and their indices:
# print(Picamera2.global_camera_info())
# You should see something like:
# [{'Id': '.../imx708@...','Num': 0, ...},
#  {'Id': '.../imx219@...','Num': 1, ...}]

# Initialize camera on CSI port 1
picam2 = Picamera2(camera_num=1)

# Configure the camera for highest quality
camera_config = picam2.create_still_configuration(
    main={"size": (4608, 2592)}  # Your camera's max resolution
)

# Apply configuration
picam2.configure(camera_config)

# Start the camera
picam2.start()

# Allow auto-exposure and AWB to settle
time.sleep(2)

try:
    print("Starting continuous capture. Press Ctrl+C to stop.")
    while True:
        # Capture image, overwriting the previous one
        picam2.capture_file("high_quality_image.jpg")
        print(f"Image captured at {time.strftime('%H:%M:%S')}")
        
        # Wait 1 second before the next capture
        time.sleep(3)

except KeyboardInterrupt:
    print("\nCapture stopped by user")

finally:
    # Clean up
    picam2.stop()
    picam2.close()
    print("Camera closed")
