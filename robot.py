import components
import constants
import magicbot
import math
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class Robot(magicbot.MagicRobot):
    # List all the components used by the robot
    controller: components.XboxController
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
        self.xbox_controller = wpilib.XboxController(constants.CONTROLLER_PORT)

    def teleopPeriodic(self):
        # Blink to indicat telop mode
        self.led.blink()
        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()
        # Use the controller input to move the robot
        self.drivetrain.move(speed=left_y, rotation=right_x)

        if self.controller.a_button():
            self.arm.extend()

        if self.controller.b_button():
            self.arm.retract()

        if self.controller.dpad_up():
            self.arm.lift()
        elif self.controller.dpad_down():
            self.arm.lower()