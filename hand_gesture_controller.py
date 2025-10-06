#!/usr/bin/env python3
"""
Hand Gesture Controller for ESP32 Servo Motor

This script uses OpenCV and MediaPipe to detect hand gestures and control
a servo motor connected to an ESP32 via serial communication.

Requirements:
- mediapipe
- opencv-python
- pyserial

Author: Hand Controlled Bot Project
"""

import cv2
import mediapipe as mp
import serial
import time
import sys
from typing import List, Tuple, Optional

class HandGestureController:
    def __init__(self, serial_port: str = None, baud_rate: int = 115200):
        """
        Initialize the hand gesture controller.
        
        Args:
            serial_port: COM port for ESP32 (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baud_rate: Serial communication baud rate
        """
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only track one hand
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
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
        self.servo_position = "UNKNOWN"  # Track actual servo position
        self.gesture_stable_count = 0    # Count stable gesture frames
        self.stability_threshold = 3     # Frames needed for stable detection (simple)
        self.last_stable_gesture = "UNKNOWN"  # Last confirmed stable gesture
        self.gesture_changed = False     # Flag to track if gesture actually changed
        
        # Simple gesture smoothing
        self.gesture_history = []        # History of recent gestures
        self.history_size = 5            # Number of recent gestures to consider (small)
        self.fist_threshold = 0.6        # Percentage of recent frames that must be FIST
        
        # Simple hold behavior
        self.servo_hold_timer = 0        # Timer to prevent rapid switching
        self.hold_delay = 20             # Frames to wait before allowing another switch (reasonable)
        
        # Hand landmark indices for fist detection
        # Fingertip landmarks
        self.fingertips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        # MCP (Metacarpophalangeal) joint landmarks
        self.mcp_joints = [3, 6, 10, 14, 18]  # Thumb, Index, Middle, Ring, Pinky
    
    def detect_fist(self, landmarks) -> bool:
        """
        Detect if the hand is making a fist based on hand landmarks.
        
        A fist is detected when most fingertips are below their corresponding MCP joints.
        More sensitive detection - only requires 3 out of 5 fingers to be closed.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            bool: True if fist is detected, False otherwise
        """
        if not landmarks:
            return False
        
        # Get image dimensions for coordinate conversion
        h, w = 480, 640  # Default camera resolution
        
        # Sensitivity parameters
        tolerance_pixels = 10  # Tolerance in pixels for detection
        required_fingers = 3   # Minimum number of fingers that must be closed (out of 5)
        
        closed_fingers = 0
        
        for i in range(len(self.fingertips)):
            fingertip_idx = self.fingertips[i]
            mcp_idx = self.mcp_joints[i]
            
            # Get landmark coordinates
            fingertip = landmarks.landmark[fingertip_idx]
            mcp = landmarks.landmark[mcp_idx]
            
            # Convert normalized coordinates to pixel coordinates
            fingertip_y = int(fingertip.y * h)
            mcp_y = int(mcp.y * h)
            
            finger_closed = False
            
            # For thumb, check x-coordinate instead of y (thumb moves horizontally)
            if i == 0:  # Thumb
                fingertip_x = int(fingertip.x * w)
                mcp_x = int(mcp.x * w)
                # Thumb is closed if fingertip is closer to palm (with tolerance)
                # More sensitive: check if thumb is significantly closer to palm
                if fingertip_x > (mcp_x - tolerance_pixels):  # More forgiving threshold
                    finger_closed = True
            else:
                # For other fingers, check if fingertip is below MCP joint (with tolerance)
                # More sensitive: add tolerance for easier detection
                if fingertip_y > (mcp_y - tolerance_pixels):  # Lower threshold for easier detection
                    finger_closed = True
            
            if finger_closed:
                closed_fingers += 1
        
        # Fist detected if enough fingers are closed
        return closed_fingers >= required_fingers
    
    def count_closed_fingers(self, landmarks) -> int:
        """
        Count how many fingers are detected as closed.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            int: Number of closed fingers (0-5)
        """
        if not landmarks:
            return 0
        
        # Get image dimensions for coordinate conversion
        h, w = 480, 640  # Default camera resolution
        
        # Sensitivity parameters (same as detect_fist)
        tolerance_pixels = 10
        closed_fingers = 0
        
        for i in range(len(self.fingertips)):
            fingertip_idx = self.fingertips[i]
            mcp_idx = self.mcp_joints[i]
            
            # Get landmark coordinates
            fingertip = landmarks.landmark[fingertip_idx]
            mcp = landmarks.landmark[mcp_idx]
            
            # Convert normalized coordinates to pixel coordinates
            fingertip_y = int(fingertip.y * h)
            mcp_y = int(mcp.y * h)
            
            finger_closed = False
            
            # For thumb, check x-coordinate instead of y
            if i == 0:  # Thumb
                fingertip_x = int(fingertip.x * w)
                mcp_x = int(mcp.x * w)
                if fingertip_x > (mcp_x - tolerance_pixels):
                    finger_closed = True
            else:
                # For other fingers, check if fingertip is below MCP joint
                if fingertip_y > (mcp_y - tolerance_pixels):
                    finger_closed = True
            
            if finger_closed:
                closed_fingers += 1
        
        return closed_fingers
    
    def smooth_gesture(self, raw_gesture):
        """
        Smooth gesture detection using rolling average of recent gestures.
        
        Args:
            raw_gesture: Raw gesture detected from current frame
            
        Returns:
            str: Smoothed gesture ("FIST", "OPEN", or "UNKNOWN")
        """
        # Add current gesture to history
        self.gesture_history.append(raw_gesture)
        
        # Keep only recent history
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)
        
        # Need at least some history to make a decision
        if len(self.gesture_history) < 5:
            return raw_gesture
        
        # Count gestures in recent history
        fist_count = self.gesture_history.count("FIST")
        open_count = self.gesture_history.count("OPEN")
        unknown_count = self.gesture_history.count("UNKNOWN")
        
        total_frames = len(self.gesture_history)
        
        # Calculate percentages
        fist_percentage = fist_count / total_frames
        open_percentage = open_count / total_frames
        
        # Determine smoothed gesture based on majority
        if fist_percentage >= self.fist_threshold:
            return "FIST"
        elif open_percentage >= self.fist_threshold:
            return "OPEN"
        else:
            # If no clear majority, return the most recent gesture
            return raw_gesture
    
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
    
    def process_frame(self, frame):
        """
        Process a single frame to detect hand gestures.
        
        Args:
            frame: OpenCV frame
            
        Returns:
            tuple: (processed_frame, gesture_detected, closed_finger_count)
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        gesture_detected = "UNKNOWN"
        closed_finger_count = 0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Count closed fingers and detect fist
                closed_finger_count = self.count_closed_fingers(hand_landmarks)
                if self.detect_fist(hand_landmarks):
                    gesture_detected = "FIST"
                else:
                    gesture_detected = "OPEN"
        
        return frame, gesture_detected, closed_finger_count
    
    def run(self):
        """
        Main loop to capture video, detect gestures, and control servo.
        """
        print("Hand Gesture Controller Started")
        print("Press 'q' to quit, 'r' to reset servo to open position")
        print("Make a fist to close servo, open hand to open servo")
        
        try:
            while True:
                # Capture frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame for hand detection
                processed_frame, raw_gesture, closed_fingers = self.process_frame(frame)
                
                # Apply gesture smoothing to reduce noise
                gesture = self.smooth_gesture(raw_gesture)
                
                # Update current gesture
                self.current_gesture = gesture
                
                # Implement simple, reliable hold behavior
                if gesture != "UNKNOWN":
                    # Decrement hold timer
                    if self.servo_hold_timer > 0:
                        self.servo_hold_timer -= 1
                    
                    # Only check for gesture changes if hold timer has expired
                    if self.servo_hold_timer == 0:
                        # Check if this is a new gesture different from the last one
                        if gesture != self.last_stable_gesture:
                            # New gesture detected, start counting stability
                            self.gesture_stable_count += 1
                            
                            # If gesture is stable enough, move servo and start hold timer
                            if self.gesture_stable_count >= self.stability_threshold:
                                self.gesture_changed = True
                                self.last_stable_gesture = gesture
                                
                                # Move servo based on gesture
                                if gesture == "FIST" and self.servo_position != "FIST":
                                    self.send_command("FIST")
                                    self.last_command_sent = "FIST"
                                    self.servo_position = "FIST"
                                    self.servo_hold_timer = self.hold_delay
                                    print("🤜 Servo moved to CLOSED position (FIST)")
                                    
                                elif gesture == "OPEN" and self.servo_position != "OPEN":
                                    self.send_command("OPEN")
                                    self.last_command_sent = "OPEN"
                                    self.servo_position = "OPEN"
                                    self.servo_hold_timer = self.hold_delay
                                    print("✋ Servo moved to OPEN position (OPEN)")
                        else:
                            # Same gesture as last stable one, reset counter
                            self.gesture_stable_count = 0
                            self.gesture_changed = False
                else:
                    # No hand detected, reset everything
                    self.gesture_stable_count = 0
                    self.gesture_changed = False
                
                # Add clean text overlay with only essential information
                cv2.putText(processed_frame, f"Hand: {self.current_gesture}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(processed_frame, f"Fingers: {closed_fingers}/5", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cv2.putText(processed_frame, f"Servo: {self.servo_position}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                # Display the frame
                cv2.imshow('Hand Gesture Controller', processed_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Reset servo to open position
                    self.send_command("OPEN")
                    self.current_gesture = "OPEN"
                    self.last_command_sent = "OPEN"
                    self.servo_position = "OPEN"
                    self.gesture_stable_count = 0
                    self.last_stable_gesture = "OPEN"
                    self.gesture_changed = False
                    self.servo_hold_timer = 0
                    print("Reset to OPEN position")
        
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
    """Main function to run the hand gesture controller."""
    print("Hand Gesture Controller for ESP32 Servo Motor")
    print("=" * 50)
    
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
        controller = HandGestureController(serial_port)
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
