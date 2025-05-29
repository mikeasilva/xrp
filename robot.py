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
    # List all the components used by the robot
    drivetrain: components.Drivetrain
    led: components.LED
    odometry: components.Odometry
    accelerometer: components.Accelerometer
    reflectance_sensor: components.ReflectanceSensor
    distance_sensor: components.DistanceSensor
    arm: components.Arm
    # What we want to see in the network tables
    left_joystick_y = magicbot.tunable(0.0)
    right_joystick_x = magicbot.tunable(0.0)

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

        # LED
        self.xrp_io = xrp.XRPOnBoardIO()

        # Gyro
        self.gyro = xrp.XRPGyro()

        # Sensors
        self.accelerometer = wpilib.BuiltInAccelerometer()
        self.reflectance_sensor = xrp.XRPReflectanceSensor()
        self.distance_sensor = xrp.XRPRangefinder()

        # Arm Servo
        self.arm_servo = xrp.XRPServo(constants.ARM_SERVO_CHANNEL)

        # Controller
        self.controller = wpilib.XboxController(constants.CONTROLLER_PORT)

    def teleopPeriodic(self):
        # Blink to indicat telop mode
        self.led.blink()
        # Get the input from the controller
        self.left_joystick_y = round(-self.controller.getLeftY(), 1)
        self.right_joystick_x = round(-self.controller.getRightX(), 1)
        # Use the controller input to move the robot
        self.drivetrain.move(speed=self.left_joystick_y, rotation=self.right_joystick_x)

        if self.controller.getAButton():
            self.arm.extend()

        if self.controller.getBButton():
            self.arm.retract()

    def disabledPeriodic(self):
        self.led.off()
        self.arm.retract()
        self.drivetrain.stop()
