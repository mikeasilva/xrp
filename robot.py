import magicbot
import components
import constants
import os
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    controller: wpilib.XboxController
    drivetrain: components.Drivetrain
    left_motor: components.XRPMotor
    right_motor: components.XRPMotor
    led: components.LED
    odometry: components.Odometry

    def createObjects(self):
        self.controller = wpilib.XboxController(constants.CONTROLLER_PORT)
        self.left_motor = components.XRPMotor(
            channel=constants.LEFT_MOTOR_CHANNEL, name="Left Motor", inverted=False
        )
        self.right_motor = components.XRPMotor(
            channel=constants.RIGHT_MOTOR_CHANNEL, name="Right Motor", inverted=True
        )
        self.drivetrain = components.Drivetrain(self.left_motor, self.right_motor)
        self.led = components.LED()
        self.odometry = components.Odometry()
        """
            gyro=wpilib.XRPGyro(),
            left_encoder=wpilib.Encoder(constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B),
            right_encoder=wpilib.Encoder(constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B),
        )
        """

    def teleopPeriodic(self):
        self.led.blink()
        self.drivetrain.set_speed(0.5)
