#!/usr/bin/env python3
"""
Direct ESP32 Test

This script directly tests communication with the ESP32.
"""

import serial
import time
import sys

def test_esp32_direct(port, baud_rate=115200):
    """Test direct communication with ESP32."""
    print(f"Testing {port} at {baud_rate} baud...")
    
    try:
        # Open serial connection
        ser = serial.Serial(port, baud_rate, timeout=2)
        time.sleep(3)  # Wait for ESP32 to initialize
        
        print(f"✅ Connected to {port}")
        
        # Clear any existing data
        ser.flushInput()
        ser.flushOutput()
        
        # Send a test command
        print("Sending 'OPEN' command...")
        ser.write(b"OPEN\n")
        ser.flush()
        
        # Wait for response
        time.sleep(1)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"📨 ESP32 Response: {response}")
        else:
            print("❌ No response from ESP32")
        
        # Try another command
        print("Sending 'FIST' command...")
        ser.write(b"FIST\n")
        ser.flush()
        
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"📨 ESP32 Response: {response}")
        else:
            print("❌ No response from ESP32")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🔧 Direct ESP32 Communication Test")
    print("=" * 40)
    
    # Test the most likely ESP32 ports
    test_ports = [
        "/dev/cu.usbserial-0001",
        "/dev/cu.SLAB_USBtoUART",
        "/dev/cu.debug-console"
    ]
    
    success = False
    
    for port in test_ports:
        print(f"\n🔍 Testing {port}...")
        if test_esp32_direct(port):
            success = True
            print(f"✅ SUCCESS! ESP32 is responding on {port}")
            break
        else:
            print(f"❌ No response from {port}")
    
    if not success:
        print("\n❌ No ESP32 communication found.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check ESP32 is connected via USB")
        print("2. Verify Arduino code was uploaded successfully")
        print("3. Check Serial Monitor in Arduino IDE for messages")
        print("4. Try different USB cable")
        print("5. Check servo connections (GPIO 18, 5V, GND)")
    else:
        print("\n🎉 ESP32 is working! Your servo should be responding to commands.")

if __name__ == "__main__":
    main()
