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

# The servo motor is connected to
# SERVO 1 = 4
# SERVO 2 = 5
SERVO_CHANNEL = 4

# PID controller constants
DISTANCE_PID = (0.1, 0, 0)
HEADING_PID = (0.1, 0, 0)
