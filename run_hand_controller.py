#!/usr/bin/env python3

import subprocess
import sys
import os

def check_mediapipe():
    try:
        import mediapipe
        return True
    except ImportError:
        return False

def main():
    print("Hand Controller Launcher")
    print("=" * 25)
    
    mediapipe_available = check_mediapipe()
    
    print(f"MediaPipe available: {'Yes' if mediapipe_available else 'No'}")
    print()
    
    if mediapipe_available:
        print("Available controllers:")
        print("1. MediaPipe Controller (Recommended)")
        print("2. Simple Controller")
        print("3. Test Serial Connection")
        print()
        
        try:
            choice = input("Enter your choice (1-3, or press Enter for MediaPipe): ").strip()
            
            if choice == "1" or choice == "":
                print("Starting MediaPipe Controller...")
                subprocess.run([sys.executable, "hand_gesture_controller.py"])
            elif choice == "2":
                print("Starting Simple Controller...")
                subprocess.run([sys.executable, "simple_hand_controller.py"])
            elif choice == "3":
                print("Testing Serial Connection...")
                subprocess.run([sys.executable, "test_serial_connection.py"])
            else:
                print("Invalid choice. Starting MediaPipe controller...")
                subprocess.run([sys.executable, "hand_gesture_controller.py"])
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("MediaPipe not available. Using Simple Controller...")
        print("To install MediaPipe, run:")
        print("  conda create -n hand_controller python=3.11")
        print("  conda activate hand_controller")
        print("  pip install mediapipe opencv-python pyserial")
        print()
        
        try:
            choice = input("Start Simple Controller? (y/n, default: y): ").strip().lower()
            if choice != "n":
                print("Starting Simple Controller...")
                subprocess.run([sys.executable, "simple_hand_controller.py"])
            else:
                print("Goodbye!")
        except KeyboardInterrupt:
            print("\nGoodbye!")

if __name__ == "__main__":
    main()