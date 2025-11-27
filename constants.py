# The deadband for the controller joysticks
CONTROLLER_DEADBAND = 0.3
# The port the controller is connected to
CONTROLLER_PORT = 0

# The XRP has the left and right motors set to
# PWM channels 0 and 1 respectively
LEFT_MOTOR_DEVICE_NUMBER = 0
RIGHT_MOTOR_DEVICE_NUMBER = 1

# The XRP has onboard encoders that are hardcoded
# to use DIO pins 4/5 and 6/7 for the left and right
LEFT_ENCODER_CHANNEL = (4, 5)
RIGHT_ENCODER_CHANNEL = (6, 7)

# The units the encoders will use for distance measurement
ENCODER_UNITS = "inches"  # "cm", "meters", "mm", "inches"

# PID controller constants
DISTANCE_PID = (0.01, 0.0, 0.001)
HEADING_PID = (0.01, 0.0, 0.001)

# Drive gear ratio and wheel diameter
COUNTS_PER_MOTOR_SHAFT_REVOLUTION = 12.0
GEAR_RATIO = (30.0 / 14.0) * (28.0 / 16.0) * (36.0 / 9.0) * (26.0 / 8.0)  # 48.75:1
COUNTS_PER_REVOLUTION = COUNTS_PER_MOTOR_SHAFT_REVOLUTION * GEAR_RATIO  # 585.0
WHEEL_DIAMETER = {
    "inches": 60.0 / 25.4,
    "mm": 60.0,
    "cm": 60.0 / 10.0,
    "meters": 60.0 / 1000.0,
}

# The track width of the drivetrain
TRACK_WIDTH = {
    "inches": 6.0,
    "mm": 6.0 * 25.4,
    "cm": 6.0 * 2.54,
    "meters": 6.0 * 0.0254,
}

# The servo motor is connected to
# SERVO 1 = 4
# SERVO 2 = 5
SERVO_CHANNEL = 4

# The default algorithm for the HuskyLens AI camera
HUSKYLENS_DEFAULT_ALGORITHM = "tag recognition"
