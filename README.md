# Hand Controlled Servo Bot

A Python-based hand gesture recognition system that controls a servo motor using an ESP32 microcontroller. The system uses MediaPipe for hand tracking and OpenCV for camera processing to detect fist gestures and control a servo motor accordingly.

## Features

- Real-time hand gesture recognition using MediaPipe
- Fist detection with configurable sensitivity
- Serial communication with ESP32 microcontroller
- Servo motor control (0 degrees = closed, 90 degrees = open)
- Stable gesture detection with hold behavior
- Clean camera interface with essential information display

## Hardware Requirements

- ESP32 DevKit V1 microcontroller
- Servo motor (SG90 or similar)
- Jumper wires
- USB cable for ESP32 programming
- Laptop/computer with camera

## Software Requirements

- Python 3.11 (recommended for MediaPipe compatibility)
- Arduino IDE (for ESP32 programming)
- Required Python packages (see requirements.txt)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hand-controlled-servo-bot.git
cd hand-controlled-servo-bot
```

### 2. Set Up Python Environment

Create a conda environment with Python 3.11:

```bash
conda create -n hand_controller python=3.11
conda activate hand_controller
pip install -r requirements.txt
```

### 3. Install Arduino Libraries

1. Open Arduino IDE
2. Install ESP32 board support:
   - Go to File > Preferences
   - Add this URL to Additional Board Manager URLs: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Go to Tools > Board > Boards Manager
   - Search for "ESP32" and install "esp32 by Espressif Systems"

3. Install ESP32Servo library:
   - Go to Tools > Manage Libraries
   - Search for "ESP32Servo" and install it

### 4. Upload Arduino Code

1. Connect ESP32 to your computer via USB
2. Open `esp32_servo_control/esp32_servo_control.ino` in Arduino IDE
3. Select your ESP32 board and COM port
4. Upload the code to the ESP32

## Hardware Connections

Connect the servo motor to the ESP32 as follows:

- Servo VCC (Red wire) → ESP32 3.3V or 5V
- Servo GND (Black/Brown wire) → ESP32 GND
- Servo Signal (Yellow/Orange wire) → ESP32 Pin 9

## Usage

### Running the Hand Controller

1. Make sure your ESP32 is connected and the Arduino code is uploaded
2. Activate the conda environment:
   ```bash
   conda activate hand_controller
   ```
3. Run the hand gesture controller:
   ```bash
   python hand_gesture_controller.py
   ```

### Controls

- **Make a fist**: Servo moves to closed position (0 degrees)
- **Open your hand**: Servo moves to open position (90 degrees)
- **Press 'r'**: Reset servo to open position
- **Press 'q'**: Quit the application

### Testing Serial Connection

To test if the ESP32 is responding to commands:

```bash
python test_serial_connection.py
```

To send direct commands to the servo:

```bash
python direct_test.py
```

## Configuration

The system includes several configuration options in `hand_gesture_controller.py`:

- `stability_threshold`: Number of frames required for stable gesture detection (default: 3)
- `history_size`: Number of recent gestures to consider for smoothing (default: 5)
- `fist_threshold`: Percentage of recent frames that must be FIST for detection (default: 0.6)
- `hold_delay`: Frames to wait before allowing another servo movement (default: 20)

## Troubleshooting

### Common Issues

1. **"No module named 'cv2'"**: Make sure you're in the correct conda environment and have installed opencv-python
2. **"No module named 'mediapipe'"**: Ensure you're using Python 3.11 and have installed mediapipe
3. **Servo not moving**: Check serial connection and ensure Arduino code is uploaded
4. **Camera not working**: Verify camera permissions and try a different camera index

### Serial Port Issues

If the system can't find the ESP32:

1. Check that the ESP32 is connected via USB
2. Verify the correct COM port in Device Manager (Windows) or System Information (Mac)
3. Make sure no other applications are using the serial port

## Project Structure

```
hand-controlled-servo-bot/
├── esp32_servo_control/
│   └── esp32_servo_control.ino    # Arduino code for ESP32
├── hand_gesture_controller.py     # Main Python application
├── simple_hand_controller.py      # Fallback controller (no MediaPipe)
├── test_serial_connection.py      # Serial communication test
├── direct_test.py                 # Direct servo control test
├── requirements.txt               # Python dependencies
├── INSTALLATION.md               # Detailed installation guide
└── README.md                     # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- MediaPipe for hand tracking capabilities
- OpenCV for computer vision processing
- ESP32 community for microcontroller support
