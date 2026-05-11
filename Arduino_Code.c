#include <EEPROM.h>
#include <HID-Project.h>
#include <HID-Settings.h>

const int pins[4] = {9, 8, 7, 6};
const int ledPin = 13;      // Existing LED (unchanged)
const int heartbeatLedPin = 2;  // New LED for Python heartbeat (pin 2)

String actions[4];  // Stores actions for each button
bool lastButtonState[4] = {HIGH, HIGH, HIGH, HIGH};
unsigned long lastDebounceTime[4] = {0, 0, 0, 0};
const unsigned long debounceDelay = 50;

// Heartbeat/LED control variables
unsigned long lastHeartbeat = 0;
const unsigned long heartbeatTimeout = 2000;  // 2 seconds timeout
bool pythonRunning = false;

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(pins[i], INPUT_PULLUP);
  }

  pinMode(ledPin, OUTPUT);           // Existing LED (pin 13)
  pinMode(heartbeatLedPin, OUTPUT);  // New heartbeat LED (pin 2)
  
  digitalWrite(ledPin, LOW);         // Start with LED off
  digitalWrite(heartbeatLedPin, LOW); // Start with heartbeat LED off

  Serial.begin(9600);

  Consumer.begin();
  Keyboard.begin();

  // Load from EEPROM
  loadFromEEPROM();

  if (actions[0] == "") {
    actions[0] = "1";
    actions[1] = "2";
    actions[2] = "3";
    actions[3] = "4";
  }

  // Send ready signal to Python
  Serial.println("READY");
  delay(100);
}

void loop() {
  // Check for incoming configuration from Python
  readSerialConfig();
  
  // Check for heartbeat signal
  checkHeartbeat();

  // Check button presses
  for (int i = 0; i < 4; i++) {
    int reading = digitalRead(pins[i]);

    if (reading != lastButtonState[i]) {
      lastDebounceTime[i] = millis();
    }

    if ((millis() - lastDebounceTime[i]) > debounceDelay) {
      if (reading == LOW) {  // Button pressed
        digitalWrite(ledPin, HIGH);  // Turn on pin 13 LED when button pressed
        
        // Send button press notification to Python
        Serial.print("PRESS:B");
        Serial.println(i + 1);
        
        // Also execute the action directly (so it works without Python)
        executeAction(actions[i]);
        
        delay(200);
        digitalWrite(ledPin, LOW);  // Turn off pin 13 LED after button press
      }
    }

    lastButtonState[i] = reading;
  }
}

// ===== CHECK HEARTBEAT FROM PYTHON =====
void checkHeartbeat() {
  if (pythonRunning) {
    // Check if heartbeat timeout has occurred
    if (millis() - lastHeartbeat > heartbeatTimeout) {
      pythonRunning = false;
      digitalWrite(heartbeatLedPin, LOW);  // Turn off heartbeat LED
      Serial.println("PYTHON:DISCONNECTED");
    }
  }
}

// ===== EXECUTE ACTION =====
void executeAction(String cmd) {
  // ===== DIRECT COPY / PASTE =====
  if (cmd == "5") {   // COPY
    Keyboard.releaseAll();
    delay(50);
    Keyboard.press(KEY_LEFT_CTRL);
    Keyboard.press('c');
    delay(100);
    Keyboard.releaseAll();
    return;
  }

  if (cmd == "6") {   // PASTE
    Keyboard.releaseAll();
    delay(50);
    Keyboard.press(KEY_LEFT_CTRL);
    Keyboard.press('v');
    delay(100);
    Keyboard.releaseAll();
    return;
  }

  // ===== CUSTOM KEYS =====
  if (cmd.startsWith("C:")) {
    handleCustom(cmd.substring(2));
    return;
  }

  int action = cmd.toInt();

  switch(action) {
    case 1: 
      Consumer.write(MEDIA_VOLUME_UP); 
      break;
    case 2: 
      Consumer.write(MEDIA_VOLUME_DOWN); 
      break;
    case 3: 
      Consumer.write(MEDIA_VOLUME_MUTE); 
      break;
    case 4: 
      Consumer.write(MEDIA_PLAY_PAUSE); 
      break;
  }
}

// ===== CUSTOM KEY HANDLER =====
void handleCustom(String combo) {
  Keyboard.releaseAll();
  delay(20);

  bool ctrl = combo.indexOf("CTRL") >= 0;
  bool alt = combo.indexOf("ALT") >= 0;
  bool shift = combo.indexOf("SHIFT") >= 0;
  bool win = combo.indexOf("WIN") >= 0;

  if (ctrl) Keyboard.press(KEY_LEFT_CTRL);
  if (alt) Keyboard.press(KEY_LEFT_ALT);
  if (shift) Keyboard.press(KEY_LEFT_SHIFT);
  if (win) Keyboard.press(KEY_LEFT_GUI);

  // ===== COPY / PASTE (Special keys) =====
  if (combo.indexOf("COPY") >= 0) {
    delay(50);
    Keyboard.press('c');
    delay(100);
    Keyboard.releaseAll();
    return;
  }

  if (combo.indexOf("PASTE") >= 0) {
    delay(50);
    Keyboard.press('v');
    delay(100);
    Keyboard.releaseAll();
    return;
  }

  // ===== FUNCTION KEYS =====
  if (combo.indexOf("F1") >= 0) Keyboard.press(KEY_F1);
  else if (combo.indexOf("F2") >= 0) Keyboard.press(KEY_F2);
  else if (combo.indexOf("F3") >= 0) Keyboard.press(KEY_F3);
  else if (combo.indexOf("F4") >= 0) Keyboard.press(KEY_F4);
  else if (combo.indexOf("F5") >= 0) Keyboard.press(KEY_F5);
  else if (combo.indexOf("F6") >= 0) Keyboard.press(KEY_F6);
  else if (combo.indexOf("F7") >= 0) Keyboard.press(KEY_F7);
  else if (combo.indexOf("F8") >= 0) Keyboard.press(KEY_F8);
  else if (combo.indexOf("F9") >= 0) Keyboard.press(KEY_F9);
  else if (combo.indexOf("F10") >= 0) Keyboard.press(KEY_F10);
  else if (combo.indexOf("F11") >= 0) Keyboard.press(KEY_F11);
  else if (combo.indexOf("F12") >= 0) Keyboard.press(KEY_F12);
  else if (combo.indexOf("TAB") >= 0) Keyboard.press(KEY_TAB);
  else if (combo.indexOf("DELETE") >= 0) Keyboard.press(KEY_DELETE);
  else if (combo.indexOf("HOME") >= 0) Keyboard.press(KEY_HOME);
  else if (combo.indexOf("END") >= 0) Keyboard.press(KEY_END);
  else if (combo.indexOf("PAGEUP") >= 0) Keyboard.press(KEY_PAGE_UP);
  else if (combo.indexOf("PAGEDOWN") >= 0) Keyboard.press(KEY_PAGE_DOWN);
  else if (combo.indexOf("ESC") >= 0) Keyboard.press(KEY_ESC);
  else if (combo.indexOf("SPACE") >= 0) Keyboard.press(' ');
  else if (combo.indexOf("ENTER") >= 0) Keyboard.press(KEY_RETURN);
  else if (combo.indexOf("BACKSPACE") >= 0) Keyboard.press(KEY_BACKSPACE);
  else if (combo.indexOf("INSERT") >= 0) Keyboard.press(KEY_INSERT);
  else if (combo.indexOf("PRTSC") >= 0) Keyboard.press(KEY_PRINTSCREEN);
  else {
    // Single character key
    String key = combo.substring(combo.lastIndexOf('+') + 1);
    if (key.length() == 1) {
      Keyboard.press(key.charAt(0));
    }
  }

  delay(100);
  Keyboard.releaseAll();
}

// ===== READ SERIAL CONFIGURATION FROM PYTHON =====
void readSerialConfig() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    // Check for heartbeat signal
    if (data == "HEARTBEAT") {
      lastHeartbeat = millis();
      if (!pythonRunning) {
        pythonRunning = true;
        digitalWrite(heartbeatLedPin, HIGH);  // Turn on heartbeat LED
        Serial.println("HEARTBEAT:ACK");
      }
      return;
    }
    
    // Check for Python start signal
    if (data == "PYTHON:START") {
      lastHeartbeat = millis();
      pythonRunning = true;
      digitalWrite(heartbeatLedPin, HIGH);  // Turn on heartbeat LED
      Serial.println("PYTHON:ACK");
      return;
    }
    
    // Check for Python stop signal
    if (data == "PYTHON:STOP") {
      pythonRunning = false;
      digitalWrite(heartbeatLedPin, LOW);  // Turn off heartbeat LED
      Serial.println("PYTHON:STOPPED");
      return;
    }

    if (data.startsWith("SET:")) {
      data.remove(0, 4);

      int index = 0;

      while (data.length() > 0 && index < 4) {
        int sep = data.indexOf('|');

        String part;
        if (sep == -1) {
          part = data;
          data = "";
        } else {
          part = data.substring(0, sep);
          data = data.substring(sep + 1);
        }

        actions[index] = part;
        index++;
      }
      
      saveToEEPROM();
      
      // Send acknowledgment to Python
      Serial.println("SET:OK");
    }
  }
}

// ===== EEPROM FUNCTIONS =====
void saveToEEPROM() {
  int addr = 0;

  for (int i = 0; i < 4; i++) {
    int len = actions[i].length();
    EEPROM.write(addr++, len);

    for (int j = 0; j < len; j++) {
      EEPROM.write(addr++, actions[i][j]);
    }
  }
  
  // Blink pin 13 LED to indicate save (existing behavior preserved)
  digitalWrite(ledPin, HIGH);
  delay(100);
  digitalWrite(ledPin, LOW);
  delay(100);
  digitalWrite(ledPin, HIGH);
  delay(100);
  digitalWrite(ledPin, LOW);
}

void loadFromEEPROM() {
  int addr = 0;

  for (int i = 0; i < 4; i++) {
    int len = EEPROM.read(addr++);

    String temp = "";
    for (int j = 0; j < len; j++) {
      temp += char(EEPROM.read(addr++));
    }

    if (temp.length() > 0)
      actions[i] = temp;
  }
}
