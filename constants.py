# General
LED_BLINK_TIME = 0.25
LOGGING_ENABLED = False


# Hardware IDs
class Ids:
    CONTROLLER = 0
    LEFT_ENCODER = (4, 5)
    LEFT_MOTOR = 0
    RIGHT_ENCODER = (6, 7)
    RIGHT_MOTOR = 1
    SERVO = 4


# Robot configuration
class Robot:
    NAME = "XRP"

    # Drivetrain geometry and motion
    GEAR_RATIO = (30.0 / 14.0) * (28.0 / 16.0) * (36.0 / 9.0) * (26.0 / 8.0)  # 48.75:1
    MAX_ROT_RPS = 6.0
    MAX_SPEED_MPS = 3.0
    TRACK_WIDTH_INCHES = 6.0
    TRACK_WIDTH_M = TRACK_WIDTH_INCHES * 0.0254
    WHEEL_DIAMETER_MM = 60.0
    WHEEL_DIAMETER_M = WHEEL_DIAMETER_MM / 1000.0
    PULSES_PER_REVOLUTION = 12.0
    TICKS_PER_REV = 585.0

    # Sensors and mechanisms
    GYRO_NOISE_THRESHOLD = 0.025
    SERVO_CHANGE = 0.025


DRIVETRAIN_CONFIG = {
    "control_loop_wait_time": 0.02,
    "deadband": 0.08,
    "heading_hold_enabled": True,
    "hold_kd": 0.0,
    "hold_ki": 0.0,
    "hold_kp": 4.0,
    "hold_max_fraction": 0.6,
    "max_rot": {
        "boost": Robot.MAX_ROT_RPS,
        "normal": 6.0,
        "precision": 4.0,
    },
    "max_rot_rps": Robot.MAX_ROT_RPS,
    "max_speed": {
        "boost": Robot.MAX_SPEED_MPS,
        "normal": 2.0,
        "precision": 1.0,
    },
    "max_speed_mps": Robot.MAX_SPEED_MPS,
    "module_locations": (),
    "rotation_accel": 12.0,
    "rotation_curve": 2.0,
    "rotation_decel": 20.0,
    "settle_rate_dps": 8.0,
    "settle_time": 0.1,
    "slew_scale": {
        "boost": 0.75,
        "normal": 1.0,
        "precision": 0.5,
    },
    "track_width": Robot.TRACK_WIDTH_M,
    "translation_accel": 6.0,
    "translation_curve": 2.0,
    "translation_decel": 12.0,
    "type": "tank",
    "units": "meters",
}
