import components
import constants
import magicbot
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class Robot(magicbot.MagicRobot):
    accelerometer: components.Accelerometer
    controller: components.XboxController
    distance_sensor = components.Distance
    drivetrain: components.DriveTrain
    gyro: components.Gyro
    led: components.LED
    reflectance_sensor: components.Reflectance
    servo: components.Servo

    def createObjects(self):
        # Controller stuff here
        self.controller_port = constants.CONTROLLER_PORT
        # Drivetrain stuff here
        self.drivetrain_left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_DEVICE_NUMBER)
        self.drivetrain_left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_A_CHANNEL, constants.LEFT_ENCODER_B_CHANNEL
        )
        self.drivetrain_right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_DEVICE_NUMBER)
        self.drivetrain_right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_A_CHANNEL, constants.RIGHT_ENCODER_B_CHANNEL
        )
        # Servo
        self.servo_channel = constants.SERVO_CHANNEL

    def teleopPeriodic(self):
        pass
