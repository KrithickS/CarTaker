#!/usr/bin/env python3
import time
import RPi.GPIO as GPIO

# — adjust this to the GPIO pin you’ve wired your servo’s signal line to —
SERVO_PIN = 18  # BCM numbering (physical pin 12)

# Angle-to–duty‑cycle conversion (0°→2.5%, 180°→12.5%)
def angle_to_duty(angle):
    return 2.5 + (angle / 180.0) * 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# 50 Hz PWM
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(angle_to_duty(0))  # start at 0°

try:
    # move to 180° (or wherever “spin” is for you)
    pwm.ChangeDutyCycle(angle_to_duty(180))
    time.sleep(2)    # run for 2 seconds
    # return to 0° (resting position)
    pwm.ChangeDutyCycle(angle_to_duty(0))
    time.sleep(0.5)  # give it time to settle
finally:
    pwm.stop()
    GPIO.cleanup()
