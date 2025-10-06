#!/usr/bin/env python3
"""
Simple Hand Gesture Controller for ESP32 Servo Motor

This is a simplified version that uses basic OpenCV for hand detection
when MediaPipe is not available. It detects hand presence and basic gestures.

Requirements:
- opencv-python
- pyserial

Author: Hand Controlled Bot Project
"""

import cv2
import serial
import time
import sys
import numpy as np
from typing import Optional

class SimpleHandController:
    def __init__(self, serial_port: str = None, baud_rate: int = 115200):
        """
        Initialize the simple hand gesture controller.
        
        Args:
            serial_port: COM port for ESP32 (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baud_rate: Serial communication baud rate
        """
        # Initialize OpenCV video capture
        self.cap = cv2.VideoCapture(0)  # Use default camera (index 0)
        
        # Check if camera is available
        if not self.cap.isOpened():
            raise RuntimeError("Error: Could not open camera. Please check your camera connection.")
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize serial communication
        self.serial_connection = None
        if serial_port:
            try:
                self.serial_connection = serial.Serial(serial_port, baud_rate, timeout=1)
                time.sleep(2)  # Wait for ESP32 to initialize
                print(f"Connected to ESP32 on {serial_port}")
            except serial.SerialException as e:
                print(f"Error connecting to ESP32: {e}")
                print("Continuing without serial connection...")
        
        # Gesture state
        self.current_gesture = "UNKNOWN"
        self.last_command_sent = None
        
        # Hand detection parameters
        self.hand_cascade = None
        self.setup_hand_detection()
        
        # Movement detection for gesture recognition
        self.prev_contours = None
        self.movement_threshold = 1000
        
    def setup_hand_detection(self):
        """Setup hand detection using OpenCV Haar cascades."""
        try:
            # Try to load hand cascade (this might not work on all systems)
            self.hand_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_hand.xml')
            if self.hand_cascade.empty():
                print("Hand cascade not available, using contour-based detection")
                self.hand_cascade = None
        except:
            print("Hand cascade not available, using contour-based detection")
            self.hand_cascade = None
    
    def detect_hand_gesture(self, frame):
        """
        Detect hand gestures using basic computer vision techniques.
        
        Args:
            frame: OpenCV frame
            
        Returns:
            str: Detected gesture ('FIST', 'OPEN', or 'UNKNOWN')
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create skin color mask
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return "UNKNOWN"
        
        # Find the largest contour (likely the hand)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Check if contour is large enough to be a hand
        area = cv2.contourArea(largest_contour)
        if area < 5000:  # Minimum area threshold
            return "UNKNOWN"
        
        # Analyze the contour to determine gesture
        gesture = self.analyze_contour(largest_contour)
        
        # Draw contour for visualization
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
        
        return gesture
    
    def analyze_contour(self, contour):
        """
        Analyze contour shape to determine gesture.
        
        Args:
            contour: OpenCV contour
            
        Returns:
            str: Detected gesture
        """
        # Approximate the contour
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Calculate contour properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Calculate solidity (area / convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Calculate aspect ratio
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Simple gesture detection based on contour properties
        # This is a basic heuristic - in practice, you'd want more sophisticated analysis
        
        # Fist detection: higher solidity (more compact shape)
        if solidity > 0.8 and aspect_ratio > 0.7 and aspect_ratio < 1.3:
            return "FIST"
        # Open hand detection: lower solidity (more spread out)
        elif solidity < 0.7 and aspect_ratio > 0.5:
            return "OPEN"
        else:
            return "UNKNOWN"
    
    def send_command(self, command: str):
        """
        Send command to ESP32 via serial communication.
        
        Args:
            command: Command to send ('FIST' or 'OPEN')
        """
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                print(f"Sent command: {command}")
            except serial.SerialException as e:
                print(f"Error sending command: {e}")
        else:
            print(f"Serial not connected. Would send: {command}")
    
    def run(self):
        """
        Main loop to capture video, detect gestures, and control servo.
        """
        print("Simple Hand Gesture Controller Started")
        print("Press 'q' to quit, 'r' to reset servo to open position")
        print("Show your hand to the camera to control the servo")
        print("Note: This is a simplified version - gesture detection may not be perfect")
        
        try:
            while True:
                # Capture frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand gesture
                gesture = self.detect_hand_gesture(frame)
                
                # Update gesture state and send commands
                if gesture != self.current_gesture and gesture != "UNKNOWN":
                    self.current_gesture = gesture
                    
                    if gesture == "FIST":
                        self.send_command("FIST")
                        self.last_command_sent = "FIST"
                    elif gesture == "OPEN":
                        self.send_command("OPEN")
                        self.last_command_sent = "OPEN"
                
                # Add text overlay to frame
                cv2.putText(frame, f"Gesture: {self.current_gesture}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Last Command: {self.last_command_sent or 'None'}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, "Press 'q' to quit, 'r' to reset", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, "Simple Mode - Basic Hand Detection", 
                           (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                
                # Display the frame
                cv2.imshow('Simple Hand Gesture Controller', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset servo to open position
                    self.send_command("OPEN")
                    self.current_gesture = "OPEN"
                    self.last_command_sent = "OPEN"
                    print("Reset to OPEN position")
                elif key == ord('f'):
                    # Force fist command
                    self.send_command("FIST")
                    self.current_gesture = "FIST"
                    self.last_command_sent = "FIST"
                    print("Forced FIST command")
                elif key == ord('o'):
                    # Force open command
                    self.send_command("OPEN")
                    self.current_gesture = "OPEN"
                    self.last_command_sent = "OPEN"
                    print("Forced OPEN command")
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            # Cleanup
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        cv2.destroyAllWindows()
        print("Cleanup completed")

def find_serial_ports():
    """
    Find available serial ports.
    
    Returns:
        list: List of available serial port names
    """
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def main():
    """Main function to run the simple hand gesture controller."""
    print("Simple Hand Gesture Controller for ESP32 Servo Motor")
    print("=" * 60)
    print("Note: This is a simplified version using basic OpenCV")
    print("For better accuracy, install MediaPipe and use hand_gesture_controller.py")
    print("=" * 60)
    
    # Find available serial ports
    available_ports = find_serial_ports()
    
    if not available_ports:
        print("No serial ports found. Running without ESP32 connection.")
        serial_port = None
    else:
        print("Available serial ports:")
        for i, port in enumerate(available_ports):
            print(f"{i + 1}. {port}")
        
        # Auto-select first USB serial port (likely ESP32)
        usb_ports = [port for port in available_ports if 'usbserial' in port or 'SLAB' in port]
        if usb_ports:
            serial_port = usb_ports[0]
            print(f"Auto-selecting ESP32 port: {serial_port}")
        else:
            serial_port = available_ports[0] if available_ports else None
            print(f"Auto-selecting first available port: {serial_port}")
    
    # Initialize and run the controller
    try:
        controller = SimpleHandController(serial_port)
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
