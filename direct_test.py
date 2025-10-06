#!/usr/bin/env python3

import serial
import time
import sys

def test_esp32_direct(port, baud_rate=115200):
    print(f"Testing {port} at {baud_rate} baud...")
    
    try:
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(3)
        
        print(f"Connected to {port}")
        
        ser.flushInput()
        ser.flushOutput()
        
        print("Sending 'OPEN' command...")
        ser.write(b"OPEN\n")
        ser.flush()
        
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"ESP32 Response: {response}")
        else:
            print("No response from ESP32")
        
        print("Sending 'FIST' command...")
        ser.write(b"FIST\n")
        ser.flush()
        
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"ESP32 Response: {response}")
        else:
            print("No response from ESP32")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Direct ESP32 Test")
    print("=" * 20)
    
    test_ports = [
        "/dev/cu.usbserial-0001",
        "/dev/cu.SLAB_USBtoUART",
        "/dev/cu.debug-console"
    ]
    
    success = False
    
    for port in test_ports:
        print(f"\nTesting {port}...")
        if test_esp32_direct(port):
            success = True
            print(f"SUCCESS! ESP32 is responding on {port}")
            break
        else:
            print(f"No response from {port}")
    
    if not success:
        print("\nNo ESP32 communication found.")
        print("\nTroubleshooting steps:")
        print("1. Check ESP32 is connected via USB")
        print("2. Verify Arduino code was uploaded successfully")
        print("3. Check Serial Monitor in Arduino IDE for messages")
        print("4. Try different USB cable")
        print("5. Check servo connections (GPIO 18, 5V, GND)")
    else:
        print("\nESP32 is working! Your servo should be responding to commands.")

if __name__ == "__main__":
    main()