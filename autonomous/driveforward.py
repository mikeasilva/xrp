import components
from magicbot import timed_state
import magicbot


class DriveForward(magicbot.AutonomousStateMachine):

    MODE_NAME = "Drive Forward"
    DEFAULT = True

    # Injected from the definition in robot.py
    drivetrain: components.DriveTrain

    @timed_state(duration=3, first=True)
    def drive_forward(self):
        self.drivetrain.go(-0.7, 0)