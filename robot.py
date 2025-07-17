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
    arm: components.Arm
    controller: components.XboxController
    drivetrain: components.TankDrive
    led: components.LED

    def createObjects(self):
        wpilib.DataLogManager.start()
        wpilib.DataLogManager.logNetworkTables(True)
        wpilib.DataLogManager.logConsoleOutput(True)
        # =============================================================
        # ARM
        # =============================================================
        self.arm_servo = xrp.XRPServo(constants.ARM_SERVO_CHANNEL)
        # =============================================================
        # CONTROLLER
        # =============================================================
        self.xbox_controller = wpilib.XboxController(constants.CONTROLLER_PORT)
        # =============================================================
        # LED
        # =============================================================
        self.xrp_led = xrp.XRPOnBoardIO()
        # =============================================================
        # MOTORS
        # =============================================================
        self.left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_CHANNEL)
        self.right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_CHANNEL)
        self.right_motor.setInverted(True)
        # Motor Encoders
        self.left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )
        # Set motor encoder distance per pulse
        distance_per_pulse = (math.pi * constants.WHEEL_DIAMETER_INCH) / (
            constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO
        )
        self.left_encoder.setDistancePerPulse(distance_per_pulse)
        self.right_encoder.setDistancePerPulse(distance_per_pulse)

    def teleopPeriodic(self):
        # Blink to indicat telop mode
        self.led.blink(duration=0.25)

        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()
        # Use the controller input to move the robot
        self.drivetrain.go(speed=left_y, rotation=right_x)
