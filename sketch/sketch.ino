#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Arduino_RouterBridge.h>

#define STEP_A 6
#define DIR_A 7
#define ENABLE_A 8

#define STEP_B 4
#define DIR_B 5
#define ENABLE_B 9

#define PEN 10
const int PEN_DELAY = 10; // delay in Pen movement in milliseconds

AccelStepper stepper_A(AccelStepper::DRIVER, STEP_A, DIR_A);
AccelStepper stepper_B(AccelStepper::DRIVER, STEP_B, DIR_B);
MultiStepper multiStepper;

const int motor_stepping = 4;
int stepper_move_speed = 200; // in mm/s
int stepper_draw_speed = 50;  // in mm/s
const float STEPPER_MAX_V = 200.0; // in mm/s
const float STEPPER_MIN_V = 1.0; // in mm/s
const float stepper_max_accel = 100;
const int steps_p_mm = 200 * motor_stepping / 2 / 20;
const int max_y = 235; // in mm
const int max_x = 265; // in mm
bool absolute_mode = true;

long timer_length = 10000; // in milliseconds
bool is_timed_out = true;
long current_timer = timer_length;
long last_time = 0;
long current_time = millis();
long delta = 0;

float current_X = 0.0;
float current_Y = 0.0;

void setup()
{
  pinMode(ENABLE_A, OUTPUT);
  pinMode(ENABLE_B, OUTPUT);
  digitalWrite(ENABLE_A, HIGH);
  digitalWrite(ENABLE_B, HIGH);

  pinMode(PEN, OUTPUT);
  digitalWrite(PEN, LOW);

  stepper_A.setMinPulseWidth(2);
  stepper_A.setMaxSpeed(stepper_move_speed * steps_p_mm);
  stepper_A.setAcceleration(stepper_max_accel);

  stepper_B.setMinPulseWidth(2);
  stepper_B.setMaxSpeed(stepper_move_speed * steps_p_mm);
  stepper_B.setAcceleration(stepper_max_accel);

  multiStepper.addStepper(stepper_A);
  multiStepper.addStepper(stepper_B);

  Bridge.begin();
  Bridge.provide("parseGcode", parseGcode);
}

void loop()
{
  last_time = current_time;
  current_time = millis();
  delta = current_time - last_time;
  current_timer += delta;
  if (current_timer >= timer_length)
  {
    is_timed_out = true;
    current_timer = timer_length;
    digitalWrite(ENABLE_A, HIGH);
    digitalWrite(ENABLE_B, HIGH);
    digitalWrite(PEN, LOW);
  }
  else
  {
    digitalWrite(ENABLE_A, LOW);
    digitalWrite(ENABLE_B, LOW);
    is_timed_out = false;
  }
}

String parseGcode(String line)
{
  current_timer = 0;
  digitalWrite(ENABLE_A, LOW);
  digitalWrite(ENABLE_B, LOW);
  if (line.startsWith("G1") || line.startsWith("G01"))
    // Draw Move
    return Gmove(line, true);
  else if (line.startsWith("G00") || line.startsWith("G0"))
    // Rapid Move
    return Gmove(line, false);
  else if (line.startsWith("M03") || line.startsWith("M3"))
    // Pen Down
    return M03();
  else if (line.startsWith("M05") || line.startsWith("M5"))
    // Pen Up
    return M05();
  else if (line.startsWith("G21"))
    // Use Millimeters (Not Implemented)
    return "ok";
  else if (line.startsWith("G90"))
    // Use Absolute
    return G90();
  else if (line.startsWith("G91"))
    // Use Relative
    return G91();
  else if (line.startsWith("G28"))
    // Use Relative
    return G28();
  else
    return "Unknown GCODE";
}

/*  Standard G move func
    speed_flag:
      true: draw_speed
      false: for move_speed
*/
String Gmove(String line, bool speed_flag)
{
  float dx = parseParam(line, 'X', current_X);
  float dy = parseParam(line, 'Y', current_Y);
  if (speed_flag)
  {
    float v = wrap(parseParam(line, 'F', stepper_draw_speed),STEPPER_MIN_V,STEPPER_MAX_V);
    setStepperSpeed(v);
  }
  else
  {
    float v = wrap(parseParam(line, 'F', stepper_move_speed),STEPPER_MIN_V,STEPPER_MAX_V);
    setStepperSpeed(v);
  }

  long pos[2];
  if (absolute_mode) {
    dx = wrap(dx,0,max_x);
    dy = wrap(dy,0,max_y);
    current_X = dx;
    current_Y = dy;
  }
  else {
    current_X += dx;
    current_Y += dy;
  }
  pos[0] = (current_X + current_Y) * steps_p_mm;
  pos[1] = (current_X - current_Y) * steps_p_mm;
  return String(pos[0]) + " " + String(pos[1]);
  multiStepper.moveTo(pos);
  multiStepper.runSpeedToPosition();
  current_timer = 0;
  return "ok";
}

// Pen Down Command
String M03()
{
  digitalWrite(PEN, LOW);
  delay(PEN_DELAY);
  return "ok";
}

// Pen Up Command
String M05()
{
  digitalWrite(PEN, HIGH);
  delay(PEN_DELAY);
  return "ok";
}

// Absolute Movement Mode
String G90()
{
  absolute_mode = true;
  return "ok";
}

// Relative Movement Mode
String G91()
{
  absolute_mode = false;
  return "ok";
}

// Home Command
String G28()
{
  stepper_A.setCurrentPosition(0);
  stepper_B.setCurrentPosition(0);
  current_X = 0.0;
  current_Y = 0.0;
  return "ok";
}

// Picks value out of gcode for given parameter
float parseParam(String line, char Param, float currentVal)
{
  int indx = line.indexOf(Param);
  if (indx == -1)
    // if new value not found, does not modify the old one
    return absolute_mode ? currentVal : 0;
  return line.substring(indx + 1).toFloat();
}

// wraps value to the min and max
float wrap(float value, int min, int max)
{
  if (value > max)
  {
    return max;
  }
  else if (value < min)
  {
    return min;
  }
  else
    return value;
}

// sets speed to move at
void setStepperSpeed(int speed)
{
  stepper_A.setMaxSpeed(speed * steps_p_mm);
  stepper_B.setMaxSpeed(speed * steps_p_mm);
}
