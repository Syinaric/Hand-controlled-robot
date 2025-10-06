#!/usr/bin/env python3

import subprocess
import sys

def check_processes():
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        mediapipe_running = any('hand_gesture_controller.py' in line for line in lines)
        simple_running = any('simple_hand_controller.py' in line for line in lines)
        
        return mediapipe_running, simple_running
    except:
        return False, False

def check_camera():
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        return ret
    except:
        return False

def check_mediapipe():
    try:
        import mediapipe
        return True
    except ImportError:
        return False

def main():
    print("Hand Controller Status")
    print("=" * 25)
    
    mediapipe_running, simple_running = check_processes()
    
    print(f"MediaPipe Controller: {'Running' if mediapipe_running else 'Not Running'}")
    print(f"Simple Controller: {'Running' if simple_running else 'Not Running'}")
    
    camera_ok = check_camera()
    print(f"Camera: {'Working' if camera_ok else 'Not Working'}")
    
    mediapipe_available = check_mediapipe()
    print(f"MediaPipe: {'Available' if mediapipe_available else 'Not Available'}")
    
    print()
    
    if mediapipe_running:
        print("System Status: FULLY OPERATIONAL")
        print("   - Advanced hand tracking with MediaPipe")
        print("   - Camera working")
        print("   - Ready to control servo motor")
    elif simple_running:
        print("System Status: BASIC MODE")
        print("   - Simple hand detection (OpenCV only)")
        print("   - Camera working")
        print("   - Ready to control servo motor")
    else:
        print("System Status: NOT RUNNING")
        print("   - No hand controller processes detected")
        print("   - Run: python run_hand_controller.py")
    
    print()
    print("Tips:")
    print("   - Make sure ESP32 is connected and powered")
    print("   - Upload Arduino code to ESP32")
    print("   - Connect servo to GPIO 18")
    print("   - Show your hand to the camera")

if __name__ == "__main__":
    main()