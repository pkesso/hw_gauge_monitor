// Pinout of arduino nano PWM
int pwm_pins[] = {3, 5, 6, 9, 10, 11};
// Size in symbols
int incoming_line[sizeof(pwm_pins)/sizeof(int)];
// Space as delimeter
const int incoming_delimeter = 32;
// \n as End Of Line
const int incoming_eol = 10;
// Init some vars...
int gauge_counter = 0;
int incoming_byte = 0;

void setup() {
  // Setting pwm pins mode to output
  for (int pwm_pin = 0; pwm_pin < sizeof(pwm_pins)/sizeof(int); pwm_pin++)
  {
    pinMode(pwm_pins[pwm_pin], OUTPUT);
  }
  // Starting serial port
  Serial.begin(115200);
  Serial.setTimeout(1);
}

// Integer concatination
int concat(int a, int b){
  char s1[20];
  char s2[20];

  // Convert both the integers to string
  sprintf(s1, "%d", a);
  sprintf(s2, "%d", b);
  // Concatenate both strings
  strcat(s1, s2);
  // To integer
  int c = atoi(s1);
  // Return the formed integer
  return c;
}

// Main loop
void loop() {
  if (Serial.available() > 0) {
    // read the incoming byte:
    delay(3);
    incoming_byte = Serial.read();
    switch (incoming_byte) {
      case incoming_delimeter:
        // if delimeter found, just incriment gauge_counter
        gauge_counter++;
        break;
      case incoming_eol:
        // if eol found, it's time to send results to the gauges
        for (int pwm_pin = 0; pwm_pin < sizeof(pwm_pins)/sizeof(int); pwm_pin++)
        {
          analogWrite(pwm_pins[pwm_pin], incoming_line[pwm_pin]);

          incoming_line[pwm_pin]=0;
        }
        gauge_counter = 0;
        Serial.print("Roger! \n");
        break;
      default:
        // in general case, we just collecting digits and concatenating them
        // if it is really a digit
        if (incoming_byte >= '0' && incoming_byte <= '9') {
          // converting ascii code to int digit
          int incoming_digit = incoming_byte - '0';
          // if it is first digit in line - no need to concatenate
          if (incoming_line[gauge_counter] == 0) {
            incoming_line[gauge_counter] = incoming_digit;
          // else - concatenaing to the digits we already have in this slot (gauge).
          } else {
            incoming_line[gauge_counter] = concat(incoming_line[gauge_counter], incoming_digit);
          }
        // if it is not a [0-9] digit
        } else {
          Serial.print("Not a digit \n");
        }
        break;
    }
  }
}
