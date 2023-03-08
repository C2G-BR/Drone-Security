const int PIN_MOTION = 3;
const int PIN_RED = 9;
const int PIN_GREEN = 6;
const int PIN_BLUE = 5;
const int PIN_BUTTON = 2;
bool buttonChange = false;
bool aware_mode = false;
bool motion = false;

void setup() {
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BLUE, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_MOTION, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_BUTTON), changePressed, HIGH);
  attachInterrupt(digitalPinToInterrupt(PIN_MOTION), motionDetected, RISING);
  Serial.begin(9600);
}

void loop() {
  if (aware_mode) {
    if (motion) {
      RGB_color(255, 0, 0);
    } else {
      RGB_color(0, 255, 0);
    }
  } else {
    RGB_color(255, 255, 255);
  }
  update_state();
  delay(100);
}

void update_state() {
  String state = "";

  if(motion) {
    state += "motion_detected";
  }else {
    state += "motion_not_detected";
  }
  state += ",";
  if(aware_mode) {
    state += "aware_mode_activated";
  }else {
    state += "aware_mode_deactivated";
  }
  
  Serial.println(state);
  Serial.flush();
}

void RGB_color(int red_light_value, int green_light_value, int blue_light_value)
{
  analogWrite(PIN_RED, red_light_value);
  analogWrite(PIN_GREEN, green_light_value);
  analogWrite(PIN_BLUE, blue_light_value);
}

void changePressed() {
  buttonChange = ! buttonChange;

  if (buttonChange) {
    aware_mode = !aware_mode;
  }
}

void motionDetected() {
  motion = ! motion;
}
