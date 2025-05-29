import components
import constants
import magicbot
import math
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    drivetrain: components.Drivetrain
    led: components.LED
    odometry: components.Odometry
    accelerometer: components.Accelerometer
    reflectance_sensor: components.ReflectanceSensor
    distance_sensor: components.DistanceSensor

    def createObjects(self):
        # Motors
        self.left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_CHANNEL)
        self.right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_CHANNEL)
        self.right_motor.setInverted(True)

        # Encoders
        self.left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )

        # Set encoder distance per pulse
        distance_per_pulse = (math.pi * constants.WHEEL_DIAMETER_INCH) / (
            constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO
        )
        self.left_encoder.setDistancePerPulse(distance_per_pulse)
        self.right_encoder.setDistancePerPulse(distance_per_pulse)

        # Controller
        self.controller = wpilib.XboxController(constants.CONTROLLER_PORT)

        # LED
        self.xrp_io = xrp.XRPOnBoardIO()

        # Gyro
        self.gyro = xrp.XRPGyro()

        # Sensors
        self.accelerometer = wpilib.BuiltInAccelerometer()
        self.reflectance_sensor = xrp.XRPReflectanceSensor()
        self.distance_sensor = xrp.XRPRangefinder()

    def teleopPeriodic(self):
        self.led.blink()
        self.drivetrain.move(
            speed=-self.controller.getLeftY(), rotation=-self.controller.getRightX()
        )
