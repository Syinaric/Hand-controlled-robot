# Hand Controlled Servo Bot

A hand gesture recognition system that controls a servo motor using an ESP32 microcontroller. Uses MediaPipe for hand tracking and OpenCV for camera processing.

## Features

- Real-time hand gesture recognition using MediaPipe
- Fist detection with configurable sensitivity
- Serial communication with ESP32 microcontroller
- Servo motor control (0 degrees = closed, 90 degrees = open)
- Stable gesture detection with hold behavior

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

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Syinaric/Hand-controlled-robot.git
cd Hand-controlled-robot
```

### 2. Set Up Python Environment

```bash
conda create -n hand_controller python=3.11
conda activate hand_controller
pip install -r requirements.txt
```

### 3. Upload Arduino Code

1. Open `esp32_servo_control/esp32_servo_control.ino` in Arduino IDE
2. Install ESP32 board support and ESP32Servo library
3. Upload the code to your ESP32

### 4. Hardware Connections

- Servo VCC (Red wire) → ESP32 5V
- Servo GND (Black/Brown wire) → ESP32 GND
- Servo Signal (Yellow/Orange wire) → ESP32 Pin 18

### 5. Run the Controller

```bash
python hand_gesture_controller.py
```

## Usage

- **Make a fist**: Servo moves to closed position (0 degrees)
- **Open your hand**: Servo moves to open position (90 degrees)
- **Press 'r'**: Reset servo to open position
- **Press 'q'**: Quit the application

## Files

- `hand_gesture_controller.py` - Main MediaPipe-based controller
- `simple_hand_controller.py` - Fallback OpenCV-only controller
- `esp32_servo_control/esp32_servo_control.ino` - Arduino code for ESP32
- `test_serial_connection.py` - Test ESP32 communication
- `direct_test.py` - Direct servo control test
- `run_hand_controller.py` - Controller launcher
- `status.py` - System status checker

## Troubleshooting

- **Camera not working**: Check camera permissions
- **Servo not moving**: Verify serial connection and Arduino code upload
- **MediaPipe errors**: Use Python 3.11 and install via conda

## License

MIT License