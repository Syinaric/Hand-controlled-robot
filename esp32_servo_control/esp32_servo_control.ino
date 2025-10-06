/*
 * ESP32 Servo Control with Serial Commands
 * 
 * This code controls a servo motor based on serial commands received from Python.
 * Commands: 'FIST' - moves servo to 90° (closed position)
 *          'OPEN' - moves servo to 0° (open position)
 * 
 * Hardware Setup:
 * - Servo signal wire to GPIO 18
 * - Servo VCC to 5V (or external power supply)
 * - Servo GND to GND
 * - ESP32 GND to Servo GND
 * 
 * Libraries Required:
 * - ESP32Servo library (install via Arduino IDE Library Manager)
 */

#include <ESP32Servo.h>

// Servo object and pin definition
Servo myServo;
const int servoPin = 18;  // GPIO pin connected to servo signal wire

// Servo position constants
const int OPEN_POSITION = 90;   // 90 degrees - open position (swapped for correct behavior)
const int CLOSED_POSITION = 0;  // 0 degrees - closed position (swapped for correct behavior)

// Serial communication
String receivedCommand = "";
bool commandComplete = false;

void setup() {
  // Initialize serial communication at 115200 baud rate
  Serial.begin(115200);
  
  // Attach servo to the specified pin
  myServo.attach(servoPin);
  
  // Move servo to initial open position
  myServo.write(OPEN_POSITION);
  
  // Print startup message
  Serial.println("ESP32 Servo Controller Ready");
  Serial.println("Waiting for commands: 'FIST' or 'OPEN'");
  Serial.println("Current position: OPEN (90°)");
  
  // Small delay to ensure servo reaches initial position
  delay(1000);
}

void loop() {
  // Check for incoming serial data
  if (Serial.available()) {
    char incomingChar = Serial.read();
    
    // Build command string
    if (incomingChar != '\n' && incomingChar != '\r') {
      receivedCommand += incomingChar;
    } else {
      // Command is complete, process it
      commandComplete = true;
    }
  }
  
  // Process complete command
  if (commandComplete) {
    processCommand(receivedCommand);
    receivedCommand = "";
    commandComplete = false;
  }
  
  // Small delay to prevent overwhelming the processor
  delay(10);
}

/*
 * Process the received serial command
 * @param command: The command string received from serial
 */
void processCommand(String command) {
  // Convert to uppercase for case-insensitive comparison
  command.toUpperCase();
  
  if (command == "FIST") {
    // Move servo to closed position (0 degrees)
    myServo.write(CLOSED_POSITION);
    Serial.println("Command: FIST - Moving to CLOSED position (0°)");
    
  } else if (command == "OPEN") {
    // Move servo to open position (90 degrees)
    myServo.write(OPEN_POSITION);
    Serial.println("Command: OPEN - Moving to OPEN position (90°)");
    
  } else {
    // Invalid command
    Serial.println("Invalid command: " + command);
    Serial.println("Valid commands: 'FIST' or 'OPEN'");
  }
}
