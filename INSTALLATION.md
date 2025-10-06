# Installation Instructions

This guide will help you set up the Hand Controlled Bot project with all required libraries and dependencies.

## Hardware Requirements

- ESP32 DevKit V1 (or compatible ESP32 board)
- Servo motor (SG90 or similar)
- Jumper wires
- USB cable for ESP32
- Laptop/computer with camera
- Optional: External 5V power supply for servo (if servo requires more current than ESP32 can provide)

## Software Requirements

### Arduino IDE Setup

1. **Install Arduino IDE**
   - Download from [arduino.cc](https://www.arduino.cc/en/software)
   - Install the latest version

2. **Install ESP32 Board Package**
   - Open Arduino IDE
   - Go to File → Preferences
   - Add this URL to "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Go to Tools → Board → Boards Manager
   - Search for "ESP32" and install "ESP32 by Espressif Systems"

3. **Install ESP32Servo Library**
   - Go to Tools → Manage Libraries
   - Search for "ESP32Servo"
   - Install "ESP32Servo" by Kevin Harrington

### Python Setup

1. **Install Python**
   - Download Python 3.8 or later from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Required Python Libraries**

   **Option A: Using pip (Recommended)**
   ```bash
   # Navigate to the project directory
   cd "Hand controlled bot"
   
   # Install all requirements
   pip install -r requirements.txt
   ```

   **Option B: Manual installation**
   ```bash
   pip install opencv-python>=4.8.0.0
   pip install mediapipe>=0.10.0
   pip install pyserial>=3.5
   pip install numpy>=1.21.0
   ```

3. **Verify Installation**
   ```bash
   python -c "import cv2, mediapipe, serial; print('All libraries installed successfully!')"
   ```

## Hardware Connections

### ESP32 to Servo Motor

| ESP32 Pin | Servo Wire | Description |
|-----------|------------|-------------|
| GPIO 18   | Signal (Yellow/Orange) | Control signal |
| 5V        | VCC (Red) | Power supply |
| GND       | GND (Brown/Black) | Ground |

**Important Notes:**
- If your servo requires more current than the ESP32 can provide, use an external 5V power supply
- Connect the external power supply's ground to both the servo ground and ESP32 ground
- Keep the signal wire connected to GPIO 18

### ESP32 to Computer

- Connect ESP32 to your computer via USB cable
- Note the COM port (Windows) or device path (Linux/Mac) for serial communication

## Finding Your ESP32 Serial Port

### Windows
1. Open Device Manager
2. Look under "Ports (COM & LPT)"
3. Find "USB-SERIAL CH340" or similar (usually COM3, COM4, etc.)

### macOS
1. Open Terminal
2. Run: `ls /dev/tty.usbserial-*` or `ls /dev/cu.usbserial-*`
3. Look for something like `/dev/tty.usbserial-0001`

### Linux
1. Open Terminal
2. Run: `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
3. Look for something like `/dev/ttyUSB0`

## Troubleshooting

### Common Issues

1. **"No module named 'cv2'"**
   - Solution: `pip install opencv-python`

2. **"No module named 'mediapipe'"**
   - Solution: `pip install mediapipe`

3. **"No module named 'serial'"**
   - Solution: `pip install pyserial`

4. **Camera not found**
   - Check if camera is being used by another application
   - Try changing camera index in the code (0, 1, 2, etc.)

5. **ESP32 not detected**
   - Check USB cable connection
   - Install CH340 drivers if needed
   - Try different USB port

6. **Servo not moving**
   - Check power connections
   - Verify servo is working with a simple test
   - Check if external power supply is needed

### Performance Tips

- Ensure good lighting for hand detection
- Keep hand in center of camera view
- Make clear, deliberate gestures
- Close other applications that might use the camera

## Next Steps

After installation, proceed to the main README.md for usage instructions and project details.
