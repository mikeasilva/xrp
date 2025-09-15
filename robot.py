import components
import constants
import elasticlib
import genie
import magicbot
from magicbot import feedback
import math
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(genie.GenieRobot):
    # The robot's magic components
    arm: components.Arm
    controller: components.XboxController
    distance_sensor: components.DistanceSensor
    drivetrain: components.DriveTrain
    led: components.LED
    line_sensor: components.LineSensor

    # Key variables
    STATE = "STARTING"
    IS_MOVING = False
    IS_TURNING = False
    ALLIANCE = "RED" if wpilib.DriverStation.Alliance.kRed else "BLUE"

    def createObjects(self):
        """Create motors and stuff here"""
        # ============================================================
        # ARM OBJECTS
        # ============================================================
        self.arm_servo_channel = constants.ARM_SERVO_CHANNEL

        # ============================================================
        # CONTROLLER OBJECTS
        # ============================================================
        self.controller_port = constants.CONTROLLER_PORT

        # ============================================================
        # DRIVETRAIN OBJECTS
        # ============================================================
        # Gyroscope
        self.drivetrain_gyro = xrp.XRPGyro()
        # Motors
        self.drivetrain_left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_CHANNEL)
        self.drivetrain_right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_CHANNEL)
        self.drivetrain_right_motor.setInverted(True)
        # Motor Encoders
        self.drivetrain_left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.drivetrain_right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )
        wheel_circumference = constants.WHEEL_DIAMETER_INCH * math.pi
        counts_per_wheel_revolution = (
            constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO
        )

        # And since we know the circumference of the wheel, we can calculate:
        distance_per_pulse = wheel_circumference / counts_per_wheel_revolution

        # We can tell the encoder to use distance per pulse
        # This changes the values returned by getDistance() to be in inches
        self.drivetrain_left_encoder.setDistancePerPulse(distance_per_pulse)
        self.drivetrain_right_encoder.setDistancePerPulse(distance_per_pulse)

        self.drivetrain_p = magicbot.tunable(default=1.0)

    def autonomousInit(self):
        """Runs all initialization code for autonomous"""
        elasticlib.select_tab("Autonomous")
        self.set_state("AUTOPILOT")
        self.led.turn_on()

    def teleopInit(self):
        """Called when teleop starts; optional"""
        elasticlib.select_tab("Teleoperated")
        self.set_state("OPERATOR CONTROLLED")

    def teleopPeriodic(self):
        self.led.blink()
        self.set_is_moving(self.drivetrain.is_moving())
        self.set_is_turning(self.drivetrain.is_turning())
        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()

        # Use the controller input to move the robot
        self.drivetrain.go(-left_y, -right_x)

        if self.controller.x_button_pressed():
            self.drivetrain.reset_gyro()
            self.drivetrain.reset_encoders()

    @feedback(key="alliance")
    def get_alliance(self):
        return self.ALLIANCE

    @feedback(key="state")
    def get_state(self):
        return self.STATE

    @feedback(key="is_moving")
    def get_is_moving(self):
        return self.IS_MOVING

    @feedback(key="is_turning")
    def get_is_turning(self):
        return self.IS_TURNING

    def set_is_moving(self, is_moving: bool):
        self.IS_MOVING = is_moving

    def set_is_turning(self, is_turning: bool):
        self.IS_TURNING = is_turning

    def set_state(self, state: str):
        self.STATE = state
