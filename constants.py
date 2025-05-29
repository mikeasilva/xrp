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

# Xbox controller port
CONTROLLER_PORT = 0

# Duration for the LED to blink on and off
LED_BLINK_DURATION_IN_SECONDS = 0.5
