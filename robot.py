import components
import constants
import magicbot
from magicbot import feedback
import os
import wpilib
import wpimath.units
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    # The robot's magic components
    controller: components.XboxController
    drivetrain: components.DriveTrain

    # Key variables
    STATE = "STARTING"
    IS_MOVING = False

    def createObjects(self):
        """Create motors and stuff here"""
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
        self.drivetrain_p = magicbot.tunable(default=1.0)

    def teleopInit(self):
        """Called when teleop starts; optional"""
        self.set_state("OPERATOR CONTROLLED")

    def teleopPeriodic(self):
        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()

        # Use the controller input to move the robot
        self.drivetrain.go(left_y, right_x)

    @feedback(key="state")
    def get_state(self):
        return self.STATE

    @feedback(key="is moving")
    def get_is_moving(self):
        return self.IS_MOVING

    def set_state(self, state):
        self.STATE = state
