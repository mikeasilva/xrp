from magicbot import AutonomousStateMachine, state, timed_state
from components.drivetrain import Drivetrain


class DriveForward(AutonomousStateMachine):
    MODE_NAME = "Drive Forward"
    DEFAULT = True

    drivetrain: Drivetrain

    @timed_state(duration=2.0, next_state="stop", first=True)
    def start(self):
        self.drivetrain.move(0.9, 0)

    @state()
    def stop(self):
        self.drivetrain.stop()
