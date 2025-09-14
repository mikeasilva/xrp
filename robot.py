import components
import constants
import elasticlib
import genie
import magicbot
from magicbot import feedback
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(genie.GenieRobot):
    # The robot's magic components
    controller: components.XboxController
    drivetrain: components.DriveTrain

    # Key variables
    STATE = "STARTING"
    IS_MOVING = False
    ALLIANCE = "RED" if wpilib.DriverStation.Alliance.kRed else "BLUE"

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

    def autonomousInit(self):
        """Runs all initialization code for autonomous"""
        elasticlib.select_tab("Autonomous")
        self.set_state("AUTOPILOT")

    def teleopInit(self):
        """Called when teleop starts; optional"""
        elasticlib.select_tab("Teleoperated")
        self.set_state("OPERATOR CONTROLLED")

    def teleopPeriodic(self):
        self.set_is_moving(self.drivetrain.is_moving())
        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()

        # Use the controller input to move the robot
        self.drivetrain.go(-left_y, -right_x)

        if self.controller.x_button_was_pressed():
            self.drivetrain.reset_gyro()
            self.drivetrain.reset_encoders()

    @feedback(key="alliance")
    def get_alliance(self):
        return self.ALLIANCE

    @feedback(key="state")
    def get_state(self):
        return self.STATE

    @feedback(key="is moving")
    def get_is_moving(self):
        return self.IS_MOVING

    def set_is_moving(self, is_moving: bool):
        self.IS_MOVING = is_moving

    def set_state(self, state: str):
        self.STATE = state
