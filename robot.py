import components
import constants
import genie
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class Robot(genie.GenieRobot):
    accelerometer: components.Accelerometer
    controller: components.XboxController
    distance_sensor = components.DistanceSensor
    drivetrain: components.DriveTrain
    gyro: components.Gyro
    # huskylens: components.HuskyLens
    led: components.LED
    reflectance_sensor: components.ReflectanceSensor
    servo: components.Servo

    def createObjects(self):
        # Controller stuff here
        self.controller_correct_for_deadband = True
        self.controller_deadband = constants.CONTROLLER_DEADBAND
        self.controller_port = constants.CONTROLLER_PORT

        # Drivetrain stuff here
        self.drivetrain_left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_DEVICE_NUMBER)
        self.drivetrain_left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL[0], constants.LEFT_ENCODER_CHANNEL[1]
        )
        self.drivetrain_right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_DEVICE_NUMBER)
        self.drivetrain_right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL[0], constants.RIGHT_ENCODER_CHANNEL[1]
        )
        self.drivetrain_encoder_units = constants.ENCODER_UNITS
        self.drivetrain_distance_pid_p = constants.DISTANCE_PID[0]
        self.drivetrain_distance_pid_i = constants.DISTANCE_PID[1]
        self.drivetrain_distance_pid_d = constants.DISTANCE_PID[2]
        self.drivetrain_heading_pid_p = constants.HEADING_PID[0]
        self.drivetrain_heading_pid_i = constants.HEADING_PID[1]
        self.drivetrain_heading_pid_d = constants.HEADING_PID[2]

        # Gyro - Passed into the gyro and accelerometer components
        self.xrp_gyro = xrp.XRPGyro()

        # HuskyLens AI Camera
        self.huskylens_default_algorithm = constants.HUSKYLENS_DEFAULT_ALGORITHM

        # Servo
        self.servo_channel = constants.SERVO_CHANNEL

    def robotInit(self):
        if constants.LOGGING_ENABLED:
            wpilib.DataLogManager.start()
            wpilib.DriverStation.startDataLog(wpilib.DataLogManager.getLog())

    def teleopPeriodic(self):
        self.controller.capture_buton_presses()
