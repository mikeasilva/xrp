# The drive mode can be either 'arcade' or 'tank'.
DRIVE_MODE = "arcade"

# The XRP has the left and right motors set to
# PWM channels 0 and 1 respectively
LEFT_MOTOR_CHANNEL = 0
RIGHT_MOTOR_CHANNEL = 1

# The gear ratio is how many times the motor shaft has to spin
# for the *wheels* to make one full rotation.
MOTOR_GEAR_RATIO = 48.75  # From datasheet

# The XRP has onboard encoders that are hardcoded
# to use DIO pins 4/5 and 6/7 for the left and right
LEFT_ENCODER_CHANNEL_A = 4
LEFT_ENCODER_CHANNEL_B = 5
RIGHT_ENCODER_CHANNEL_A = 6
RIGHT_ENCODER_CHANNEL_B = 7
# The encoder has this many ticks per revolution *of the motor shaft*
# (*not* the wheel itself)
ENCODER_RESOLUTION = 12  # From datasheet

# Based on the datasheet, the wheel diameter is 60mm
WHEEL_DIAMETER_MM = 60
WHEEL_DIAMETER_INCH = WHEEL_DIAMETER_MM / 25.4  # Wheel diameter in inches

# The controller is connected to the XRP on port 0
CONTROLLER_PORT = 0

# How long should the LED be on or off?
LED_BLINK_DURATION_IN_SECONDS = 0.5

# The servo motor is connected to PWM channel 4
ARM_SERVO_CHANNEL = 4

# How much do you want to shift the servo by when you press the button?
ARM_SERVO_SHIFT_BY = 0.02

# Distance in inches to avoid an obstacle
CRASH_AVOIDANCE_DISTANCE = 12.0
