from math import pi

PULSES_PER_REVOLUTION = 12.0
GEAR_RATIO = (30.0 / 14.0) * (28.0 / 16.0) * (36.0 / 9.0) * (26.0 / 8.0)  # 48.75:1
WHEEL_DIAMETER_MM = 60.0
WHEEL_DIAMETER_M = WHEEL_DIAMETER_MM / 1000.0
### Distance per pulse is pi * wheel diameter / pulses per revolution * gear ratio
DISTANCE_PER_PULSE = pi * WHEEL_DIAMETER_M / (PULSES_PER_REVOLUTION * GEAR_RATIO)


class Ids:
    LEFT_MOTOR = 0
    RIGHT_MOTOR = 1
    LEFT_ENCODER = (4, 5)
    RIGHT_ENCODER = (6, 7)
    SERVO = 4
    GAMEPAD = 0


LEFT_INVERTED = False
RIGHT_INVERTED = not LEFT_INVERTED
