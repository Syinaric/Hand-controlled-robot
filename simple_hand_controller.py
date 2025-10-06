#!/usr/bin/env python3

import cv2
import serial
import time
import sys
import numpy as np
from typing import Optional

class SimpleHandController:
    def __init__(self, serial_port: str = None, baud_rate: int = 115200):
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
        
        self.hand_cascade = None
        self.setup_hand_detection()
        
        self.prev_contours = None
        self.movement_threshold = 1000
        
    def setup_hand_detection(self):
        try:
            self.hand_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_hand.xml')
            if self.hand_cascade.empty():
                print("Using contour-based detection")
                self.hand_cascade = None
        except:
            print("Using contour-based detection")
            self.hand_cascade = None
    
    def detect_hand_gesture(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return "UNKNOWN"
        
        largest_contour = max(contours, key=cv2.contourArea)
        
        area = cv2.contourArea(largest_contour)
        if area < 5000:
            return "UNKNOWN"
        
        gesture = self.analyze_contour(largest_contour)
        
        cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
        
        return gesture
    
    def analyze_contour(self, contour):
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        if solidity > 0.8 and aspect_ratio > 0.7 and aspect_ratio < 1.3:
            return "FIST"
        elif solidity < 0.7 and aspect_ratio > 0.5:
            return "OPEN"
        else:
            return "UNKNOWN"
    
    def send_command(self, command: str):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                print(f"Sent: {command}")
            except serial.SerialException as e:
                print(f"Error: {e}")
        else:
            print(f"Would send: {command}")
    
    def run(self):
        print("Simple Controller Started")
        print("Press 'q' to quit, 'r' to reset")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Camera error")
                    break
                
                frame = cv2.flip(frame, 1)
                gesture = self.detect_hand_gesture(frame)
                
                if gesture != self.current_gesture and gesture != "UNKNOWN":
                    self.current_gesture = gesture
                    
                    if gesture == "FIST":
                        self.send_command("FIST")
                        self.last_command_sent = "FIST"
                    elif gesture == "OPEN":
                        self.send_command("OPEN")
                        self.last_command_sent = "OPEN"
                
                cv2.putText(frame, f"Gesture: {self.current_gesture}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Last: {self.last_command_sent or 'None'}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                cv2.imshow('Simple Controller', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.send_command("OPEN")
                    self.current_gesture = "OPEN"
                    self.last_command_sent = "OPEN"
                    print("Reset")
                elif key == ord('f'):
                    self.send_command("FIST")
                    self.current_gesture = "FIST"
                    self.last_command_sent = "FIST"
                    print("FIST")
                elif key == ord('o'):
                    self.send_command("OPEN")
                    self.current_gesture = "OPEN"
                    self.last_command_sent = "OPEN"
                    print("OPEN")
        
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
    print("Simple Hand Controller")
    print("=" * 25)
    
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
        controller = SimpleHandController(serial_port)
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()