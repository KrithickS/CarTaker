# 🚗 Caretaker – Automated Car Window Override & Dashcam System for Passenger Safety

**A real-time Raspberry Pi-based emergency safety system that prevents heatstroke and suffocation during vehicle entrapments by combining facial/emotion detection, environmental sensing, and automatic window control.**

---

## 📌 Table of Contents
- [About the Project](#about-the-project)
- [Project Motivation](#project-motivation)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Hardware Components](#hardware-components)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Results](#results)
- [Future Work](#future-work)
- [Contributors](#contributors)
- [License](#license)

---

## 🧠 About the Project

**Caretaker** is a Raspberry Pi 5-based system that automatically overrides car windows and records external events to prevent fatalities in car entrapment scenarios. The system:
- Detects human presence and emotional state using onboard ML models.
- Monitors CO₂ and temperature in real-time.
- Triggers window-opening mechanisms during emergencies.
- Alerts the owner and securely stores dashcam footage on a remote NAS.

---

## 💡 Project Motivation

Numerous fatalities have been reported due to car entrapment caused by door malfunctions or accidents. Incidents involving children, elderly, and pets highlight the need for an **automated, intelligent, and locally responsive system**.

---

## 🛠️ System Architecture

[Face & Emotion Detection] [Temp & CO₂ Sensors]
\ /
[Raspberry Pi 5] (Decision Engine)
/
[Window Trigger + Alerts] [Dashcam Recording ➝ NAS]


---

## ✨ Features

- Real-time **face and emotion detection** (YOLOv5 + CNN).
- Automated **window override** mechanism.
- Continuous monitoring of **temperature** and **CO₂**.
- External **dashcam footage recording** with secure NAS sync.
- **Offline-first** processing with local decision-making.
- Secure **video storage** with AES-256 encryption via TrueNAS.

---

## ⚙️ Tech Stack

- Raspberry Pi 5 (Python)
- YOLOv5 (PyTorch-based)
- CNN for Emotion Recognition
- DHT22 (Temperature sensor)
- MQ135 (CO₂ sensor)
- Libcamera for video
- Tailscale for secure NAS connection
- TrueNAS SCALE for storage
- SMB + rsync + systemd for file sync

---

## 🔩 Hardware Components

- Raspberry Pi 5
- Raspberry Pi Camera Module 3 (Wide)
- DHT22 Temperature Sensor
- MQ135 CO₂ Sensor
- Power Window Motor Interface
- NAS with TrueNAS SCALE
- Internet connection (for NAS sync only)

---
## 🧪 Setup Instructions

Follow these steps to set up the Caretaker system on your Raspberry Pi 5 and NAS environment:

### 1️⃣ Raspberry Pi Setup

1. **Update your system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install required dependencies:**
   ```bash
   sudo apt install -y python3-pip libcamera-dev rsync tailscale
   pip3 install torch torchvision opencv-python dlib
   ```

3. **Enable interfaces:**
   - Open Raspberry Pi Configuration (`sudo raspi-config`)
   - Enable:  
     - Camera Interface  
     - I2C Interface (if required by sensors)  
     - SPI Interface (optional, if used for window motor)

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/Caretaker.git
cd Caretaker
```

Replace `yourusername` with your GitHub username.

---

### 3️⃣ Setup Crontab for Auto Dashcam Start

```bash
crontab -e
```

Add the following line to start the dashcam recording on reboot:
```bash
@reboot python3 /home/pi/Caretaker/src/start_dashcam.py &
```

---

### 4️⃣ Setup Systemd Service for NAS Sync

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/caretaker-sync.service
```

Paste this:
```ini
[Unit]
Description=Caretaker Video Sync Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/Caretaker/src/sync_to_nas.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start it:
```bash
sudo systemctl enable caretaker-sync.service
sudo systemctl start caretaker-sync.service
```

---

### 5️⃣ NAS Setup with TrueNAS SCALE

1. Install [TrueNAS SCALE](https://www.truenas.com/download-truenas-scale/) on your storage server.
2. Create two datasets:
   - `recordings` – for dashcam footage
   - `general` – for config/logs
3. Enable **SMB share** for `/recordings`.
4. Set appropriate permissions.
5. Connect Raspberry Pi via **Tailscale**:
   ```bash
   tailscale up
   ```

---

### 6️⃣ Setup rsync for NAS Sync

Add this to your script (`sync_to_nas.py`):

```python
import os
os.system("ping -c 1 google.com > /dev/null 2>&1 && rsync -av --remove-source-files /home/pi/recordings/ /mnt/nas/recordings/")
```

Ensure `/mnt/nas/recordings/` is mounted (via SMB or CIFS in `/etc/fstab`).

---

✅ Your system should now:
- Record external dashcam footage at boot
- Monitor passengers and environment
- Sync footage to NAS every 5 minutes when internet is available

▶️ Usage
Startup: When RPi boots, crontab triggers dashcam, systemd starts file sync.

Processing: Sensor and camera data continuously monitored.

Triggering: If unsafe CO₂/temperature or distressed emotion detected, windows open, alerts sent.

Footage: Dashcam footage is sent to NAS every 5 minutes if internet is available.

📊 Results
Emotion Recognition: Accuracy: 66% (test), 82% (frontal face), 76% (profile)

Face Detection (YOLOv5): 65.8% training accuracy, 64.7% validation

System Performance: Fast local decision-making with secure data handling

Storage: AES-256-GCM encryption on TrueNAS, footage recycled every 48 hrs

🚀 Future Work
Improve low-light accuracy for emotion detection

Add audio alerts + external speaker support

Mobile app integration for real-time alerts

Solar-powered backup for offline functioning

👥 Contributors
Krithick S – krithick.s2022@vitstudent.ac.in

R. Sacheev Krishanu – sacheevkrishanu.r2022@vitstudent.ac.in

Abishek Devadoss – abishek.devadoss2022@vitstudent.ac.in
