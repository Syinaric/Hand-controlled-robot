#!/usr/bin/env python3

import serial
import time
import sys

def find_serial_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def test_serial_connection(port, baud_rate=115200):
    try:
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(2)
        
        print(f"Connected to {port} at {baud_rate} baud")
        print("Sending test commands...")
        
        commands = ["OPEN", "FIST", "OPEN", "FIST", "OPEN"]
        
        for i, command in enumerate(commands, 1):
            print(f"\nTest {i}/5: Sending '{command}'")
            ser.write(f"{command}\n".encode())
            
            time.sleep(1)
            
            if ser.in_waiting:
                response = ser.readline().decode().strip()
                print(f"ESP32 response: {response}")
            else:
                print("No response from ESP32")
            
            time.sleep(1)
        
        print("\nTest completed successfully!")
        print("If you saw the servo moving, your connection is working!")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"Error connecting to {port}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    print("ESP32 Serial Test")
    print("=" * 20)
    
    available_ports = find_serial_ports()
    
    if not available_ports:
        print("No serial ports found.")
        print("Make sure your ESP32 is connected and drivers are installed.")
        return
    
    print("Available serial ports:")
    for i, port in enumerate(available_ports):
        print(f"{i + 1}. {port}")
    
    print("\nTesting all available ports...")
    success = False
    for port in available_ports:
        print(f"\nTesting {port}...")
        if test_serial_connection(port):
            success = True
            break
    
    if not success:
        print("\nNo working connection found.")
        print("Please check:")
        print("1. ESP32 is connected via USB")
        print("2. Correct drivers are installed")
        print("3. ESP32 code is uploaded and running")
        print("4. ESP32 is powered on")

if __name__ == "__main__":
    main()