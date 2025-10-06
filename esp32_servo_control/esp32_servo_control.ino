/*
 * ESP32 Servo Control
 */

#include <ESP32Servo.h>

Servo myServo;
const int servoPin = 18;
const int OPEN_POSITION = 90;
const int CLOSED_POSITION = 0;
String receivedCommand = "";
bool commandComplete = false;

void setup() {
  Serial.begin(115200);
  myServo.attach(servoPin);
  myServo.write(OPEN_POSITION);
  Serial.println("Ready");
  delay(1000);
}

void loop() {
  if (Serial.available()) {
    char incomingChar = Serial.read();
    
    if (incomingChar != '\n' && incomingChar != '\r') {
      receivedCommand += incomingChar;
    } else {
      commandComplete = true;
    }
  }
  
  if (commandComplete) {
    processCommand(receivedCommand);
    receivedCommand = "";
    commandComplete = false;
  }
  
  delay(10);
}

void processCommand(String command) {
  command.toUpperCase();
  
  if (command == "FIST") {
    myServo.write(CLOSED_POSITION);
    Serial.println("FIST");
  } else if (command == "OPEN") {
    myServo.write(OPEN_POSITION);
    Serial.println("OPEN");
  }
}
