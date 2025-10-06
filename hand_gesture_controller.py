#!/usr/bin/env python3

import cv2
import mediapipe as mp
import serial
import time
import sys
from typing import List, Tuple, Optional

class HandGestureController:
    def __init__(self, serial_port: str = None, baud_rate: int = 115200):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise RuntimeError("Camera not available")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.serial_connection = None
        if serial_port:
            try:
                self.serial_connection = serial.Serial(serial_port, baud_rate, timeout=1)
                time.sleep(2)
                print(f"Connected to {serial_port}")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
        
        self.current_gesture = "UNKNOWN"
        self.last_command_sent = None
        self.servo_position = "UNKNOWN"
        self.gesture_stable_count = 0
        self.stability_threshold = 3
        self.last_stable_gesture = "UNKNOWN"
        self.gesture_changed = False
        
        self.gesture_history = []
        self.history_size = 5
        self.fist_threshold = 0.6
        
        self.servo_hold_timer = 0
        self.hold_delay = 20
        
        self.fingertips = [4, 8, 12, 16, 20]
        self.mcp_joints = [3, 6, 10, 14, 18]
    
    def detect_fist(self, landmarks) -> bool:
        if not landmarks:
            return False
        
        h, w = 480, 640
        tolerance_pixels = 10
        required_fingers = 3
        closed_fingers = 0
        
        for i in range(len(self.fingertips)):
            fingertip_idx = self.fingertips[i]
            mcp_idx = self.mcp_joints[i]
            
            fingertip = landmarks.landmark[fingertip_idx]
            mcp = landmarks.landmark[mcp_idx]
            
            fingertip_y = int(fingertip.y * h)
            mcp_y = int(mcp.y * h)
            
            finger_closed = False
            
            if i == 0:
                fingertip_x = int(fingertip.x * w)
                mcp_x = int(mcp.x * w)
                if fingertip_x > (mcp_x - tolerance_pixels):
                    finger_closed = True
            else:
                if fingertip_y > (mcp_y - tolerance_pixels):
                    finger_closed = True
            
            if finger_closed:
                closed_fingers += 1
        
        return closed_fingers >= required_fingers
    
    def count_closed_fingers(self, landmarks) -> int:
        if not landmarks:
            return 0
        
        h, w = 480, 640
        tolerance_pixels = 10
        closed_fingers = 0
        
        for i in range(len(self.fingertips)):
            fingertip_idx = self.fingertips[i]
            mcp_idx = self.mcp_joints[i]
            
            fingertip = landmarks.landmark[fingertip_idx]
            mcp = landmarks.landmark[mcp_idx]
            
            fingertip_y = int(fingertip.y * h)
            mcp_y = int(mcp.y * h)
            
            finger_closed = False
            
            if i == 0:
                fingertip_x = int(fingertip.x * w)
                mcp_x = int(mcp.x * w)
                if fingertip_x > (mcp_x - tolerance_pixels):
                    finger_closed = True
            else:
                if fingertip_y > (mcp_y - tolerance_pixels):
                    finger_closed = True
            
            if finger_closed:
                closed_fingers += 1
        
        return closed_fingers
    
    def smooth_gesture(self, raw_gesture):
        self.gesture_history.append(raw_gesture)
        
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)
        
        if len(self.gesture_history) < 5:
            return raw_gesture
        
        fist_count = self.gesture_history.count("FIST")
        open_count = self.gesture_history.count("OPEN")
        unknown_count = self.gesture_history.count("UNKNOWN")
        
        total_frames = len(self.gesture_history)
        
        fist_percentage = fist_count / total_frames
        open_percentage = open_count / total_frames
        
        if fist_percentage >= self.fist_threshold:
            return "FIST"
        elif open_percentage >= self.fist_threshold:
            return "OPEN"
        else:
            return raw_gesture
    
    def send_command(self, command: str):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                print(f"Sent: {command}")
            except serial.SerialException as e:
                print(f"Error: {e}")
        else:
            print(f"Would send: {command}")
    
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_detected = "UNKNOWN"
        closed_finger_count = 0
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                closed_finger_count = self.count_closed_fingers(hand_landmarks)
                if self.detect_fist(hand_landmarks):
                    gesture_detected = "FIST"
                else:
                    gesture_detected = "OPEN"
        
        return frame, gesture_detected, closed_finger_count
    
    def run(self):
        print("Controller Started")
        print("Press 'q' to quit, 'r' to reset")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Camera error")
                    break
                
                frame = cv2.flip(frame, 1)
                processed_frame, raw_gesture, closed_fingers = self.process_frame(frame)
                gesture = self.smooth_gesture(raw_gesture)
                self.current_gesture = gesture
                
                if gesture != "UNKNOWN":
                    if self.servo_hold_timer > 0:
                        self.servo_hold_timer -= 1
                    
                    if self.servo_hold_timer == 0:
                        if gesture != self.last_stable_gesture:
                            self.gesture_stable_count += 1
                            
                            if self.gesture_stable_count >= self.stability_threshold:
                                self.gesture_changed = True
                                self.last_stable_gesture = gesture
                                
                                if gesture == "FIST" and self.servo_position != "FIST":
                                    self.send_command("FIST")
                                    self.last_command_sent = "FIST"
                                    self.servo_position = "FIST"
                                    self.servo_hold_timer = self.hold_delay
                                    print("FIST")
                                    
                                elif gesture == "OPEN" and self.servo_position != "OPEN":
                                    self.send_command("OPEN")
                                    self.last_command_sent = "OPEN"
                                    self.servo_position = "OPEN"
                                    self.servo_hold_timer = self.hold_delay
                                    print("OPEN")
                        else:
                            self.gesture_stable_count = 0
                            self.gesture_changed = False
                else:
                    self.gesture_stable_count = 0
                    self.gesture_changed = False
                
                cv2.putText(processed_frame, f"Hand: {self.current_gesture}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(processed_frame, f"Fingers: {closed_fingers}/5", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cv2.putText(processed_frame, f"Servo: {self.servo_position}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                cv2.imshow('Hand Controller', processed_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.send_command("OPEN")
                    self.current_gesture = "OPEN"
                    self.last_command_sent = "OPEN"
                    self.servo_position = "OPEN"
                    self.gesture_stable_count = 0
                    self.last_stable_gesture = "OPEN"
                    self.gesture_changed = False
                    self.servo_hold_timer = 0
                    print("Reset")
        
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.cap:
            self.cap.release()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        cv2.destroyAllWindows()
        print("Cleanup completed")

def find_serial_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def main():
    print("Hand Controller")
    print("=" * 20)
    
    available_ports = find_serial_ports()
    
    if not available_ports:
        print("No serial ports found")
        serial_port = None
    else:
        print("Available ports:")
        for i, port in enumerate(available_ports):
            print(f"{i + 1}. {port}")
        
        usb_ports = [port for port in available_ports if 'usbserial' in port or 'SLAB' in port]
        if usb_ports:
            serial_port = usb_ports[0]
            print(f"Using: {serial_port}")
        else:
            serial_port = available_ports[0] if available_ports else None
            print(f"Using: {serial_port}")
    
    try:
        controller = HandGestureController(serial_port)
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()