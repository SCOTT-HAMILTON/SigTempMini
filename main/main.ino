#include <SoftwareSerial.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

// Define the pins for software serial
const int UART_SIG_RX = 10;
const int UART_SIG_TX = 11;
SoftwareSerial mySerial(UART_SIG_RX, UART_SIG_TX); // RX, TX
const int tempExtPin = A0;
const int tempIntPin = A1;
const int battPin = A2;
const int LED_PIN = 9;

const float Tmin = -60.0;
const float Tmax = 60.0;

float tempExt = 0;
float tempInt = 0;
float voltBatt = 0;

int send_counter = 0;
const int send_counter_threshold = 128;

void blink(int n) {
  for (int i=0; i < n; ++i) {
    digitalWrite(LED_PIN, LOW);
    delay(150);
    digitalWrite(LED_PIN, HIGH);
    delay(150);
  }
}

// Function to wait for "OK" response with timeout
bool waitForOK(unsigned long timeout = 5000) {
  unsigned long startTime = millis();
  char lastChar = 0;

  while (millis() - startTime < timeout) {
    if (mySerial.available() > 0) {
      char inChar = mySerial.read();
      
      // Check for "OK" sequence
      if (lastChar == 'O' && inChar == 'K') {
        return true;
      }
      
      // Update last character
      lastChar = inChar;
    }

    // Small delay to prevent busy-waiting
    delay(10);
  }

  // Timeout occurred
  return false;
}

struct Data {
  float tempInt;
  float tempExt;
  float battVolt;
};

struct Data meas_data(){
  analogReference(INTERNAL);
  tempExt = filter(tempExt, meas_pin_raw(tempExtPin, 1.1)*100.0);
  analogReference(DEFAULT);
  float voltInt = meas_pin_raw(tempIntPin, 3.3);
  tempInt = filter(tempInt, Th(voltInt/3.3));
  voltBatt = filter(voltBatt, meas_pin_raw(battPin, 3.3)/0.2188);
  return Data {
    tempInt, tempExt, voltBatt
  };
}

int bound(int min, int max, int val) {
  if (val > max) {
    return max;
  }
  if (val < min) {
    return min;
  }
  return val;
}

void send_data(struct Data data){
  blink(2);
  // Calculate the integer values
  int zz = bound(0, 0xFFF, int(round((data.tempInt - Tmin)/(Tmax-Tmin)*0xFFF)));  // ZZ = int(round(tempInt * 100))
  int yy = bound(0, 0xFFF, int(round((data.tempExt - Tmin)/(Tmax-Tmin)*0xFFF)));  // 0 -> -60°C, 
  int xx = bound(0, 0xFF, int(round(data.battVolt * 0xFF / 15.0)));  // XX = int(round(battVolt * 255.0 / 15.0)) 
  
  // Convert the integers to uppercase hex byte representations
  char zzHex[4];
  char yyHex[4];
  char xxHex[3];

  snprintf(zzHex, 4, "%03X", zz);  // Convert ZZ to 2-digit uppercase hex
  snprintf(yyHex, 4, "%03X", yy);  // Convert YY to 2-digit uppercase hex
  snprintf(xxHex, 3, "%02X", xx);  // Convert XX to 2-digit uppercase hex

  // Create the payload string
  char payload[15];
  sprintf(payload, "AT$SF=%s%s%s", xxHex, yyHex, zzHex);

  // Print the payload to the Serial Monitor for verification
  Serial.print("Sending `");
  Serial.print(payload);
  Serial.println("`");
  
  mySerial.println(payload);
  if (waitForOK(15000)) {
    blink(4);
    Serial.println("Data sent !");
  } else {
    blink(3);
    Serial.println("Failed to send payload !");
  }
}

void wakeUp(){}

void sleep(){
  power_adc_disable();
  power_spi_disable();
  power_timer0_disable();
  power_timer1_disable();

  // Configurer le Watchdog Timer pour 8 secondes
  setup_watchdog(9);

  // Activer le mode de veille
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();

  // Attacher une interruption à la broche 10 pour réveiller l'Arduino
  attachInterrupt(digitalPinToInterrupt(UART_SIG_RX), wakeUp, LOW);

  // Aller en mode veille
  sleep_mode();

  // Désactiver le mode de veille après réveil
  sleep_disable();
  detachInterrupt(digitalPinToInterrupt(UART_SIG_RX));

  // Réactiver les périphériques
  power_all_enable(); // Réactive tous les périphériques

  // Ou réactiver individuellement si vous voulez plus de contrôle
  power_adc_enable();
  power_spi_enable();
  power_timer0_enable();
  power_timer1_enable();
}

void setup_watchdog(int timerPrescaler) {
  if (timerPrescaler > 9 ) timerPrescaler = 9; // Limiter à 8 secondes

  byte bb = timerPrescaler & 7;
  if (timerPrescaler > 7) bb |= (1<<5); // Configurer le bit 5 pour les valeurs > 7

  // Désactiver le Watchdog Timer
  wdt_reset();
  wdt_disable();

  // Configurer le Watchdog Timer
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  WDTCSR = (1<<WDIE) | bb;
  wdt_reset();
}

ISR(WDT_vect) {
  wdt_disable(); // Désactiver le Watchdog Timer après réveil
}

float meas_pin_raw(int pin, float ref) {
  unsigned long int S = 0;
  const int N = 2000;
  for (int i = 0; i < N; ++i) {
    int sensorValue = analogRead(pin);  // Read the analog value
    S += sensorValue;
  }
  float v = (ref*(float)S/(float)N/1023.0); // [m°]
  return v;
}

/* float meas_pin(int pin, float ref) { */
/*   float v = 0; */
/*   int N = 4; */
/*   for (int j = 0; j < N; ++j) { */
/*     v += meas_pin_raw(pin, ref); */
/*     delay(1000/N); */
/*   } */
/*   return v/(float)N; */
/* } */

float horner(float x, float coeffs[], int degree) {
  float result = coeffs[0]; // Start with the highest-degree coefficient
  for (int i = 1; i <= degree; i++) {
    result = result * x + coeffs[i];
  }
  return result;
}

float Th(float H) {
  float B = 4887.0;
  float coeffs[] = {  0.12215323, -0.51134901,  0.81893543, -0.67687026,  0.31558427,
       -0.09557197,  0.07739318 };
  int degree = 6; // Degree of the polynomial
  float result = horner(H, coeffs, degree);
  return result*B-273.15;
}

/* const float nu = 0.05; // fréqence réduite du filtre du 1er ordre */
/* const float Tr = 1/(2*3.14159265*nu); */
/* const float alpha = 1/(1+Tr); */
const float alpha = 0.73;

float filter(float val, float newval) {
  return alpha*val+(1-alpha)*newval;
}

void print_data(struct Data data){
  Serial.print(data.tempExt, 8);
  Serial.print(", ");
  Serial.print(data.tempInt, 8);
  Serial.print(", ");
  Serial.println(data.battVolt, 8);
}

void setup() {
  // Initialize hardware serial for debugging
  Serial.begin(74880);
  Serial.println("Arduino UART Shell Prompt");

  // Initialize software serial for UART device
  mySerial.begin(9600);

  analogReference(INTERNAL);
  pinMode(UART_SIG_RX, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  analogReference(INTERNAL);
  tempExt = meas_pin_raw(tempExtPin, 1.1)*100.0;
  analogReference(DEFAULT);
  float voltInt = meas_pin_raw(tempIntPin, 3.3);
  tempInt = Th(voltInt/3.3);
  voltBatt = meas_pin_raw(battPin, 3.3)/0.2188;
  
  Serial.println("Ensuring LSM100A is ready...");
  while (true) {
    mySerial.println("AT");
    if (waitForOK(1000)) {
      break;
    }
  }
  Serial.println("LSM100A is ready !");

  struct Data data = meas_data();
  print_data(data);
  send_data(data);
}


void loop() {
  ++send_counter;
  Serial.println("Measuring data...");
  struct Data data = meas_data();
  print_data(data);
  if (send_counter >= send_counter_threshold) {
    send_counter = 0;
    send_data(data);
  } else {
    Serial.print(send_counter);
    Serial.print("/");
    Serial.println(send_counter_threshold);
  }
  // Check if there is data available from the hardware serial (your computer)
  if (Serial.available()) {
    // Read the command from the hardware serial
    String command = Serial.readStringUntil('\n'); // Read until newline

    // Debug: Print the raw input
    Serial.print("Raw input: '");
    Serial.print(command);
    Serial.println("'");

    command.replace("\r", ""); // Remove all carriage returns
    command.replace("\n", ""); // Remove all newlines
    command.trim(); // Remove any extra whitespace (optional, for cleanliness)

    // Send the command to the UART device
    Serial.print("Sending command: `");
    Serial.print(command);
    Serial.println("`");
    mySerial.print(command);
    mySerial.print("\r"); // Append carriage return (if required by your UART device)

    // Wait for the UART device to respond
    delay(100); // Small delay to allow the UART device to process the command
  }
  // Read and print the response from the UART device
  bool read = false;
  while (mySerial.available()) {
    char c = mySerial.read();
    Serial.write(c); // Print to hardware serial for debugging
    read = true;
  }
  if (read) {
    Serial.println(); // Print a newline after the response
  }
  Serial.println("Sleeping...");
  delay(100);
  digitalWrite(LED_PIN, LOW);
  sleep();
  digitalWrite(LED_PIN, HIGH);
  Serial.println("Woke up!");
}
