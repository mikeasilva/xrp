import components
import magicbot


class DriveForward(magicbot.AutonomousStateMachine):
    MODE_NAME = "Drive Forward"
    DEFAULT = True

    drivetrain: components.Drivetrain

    @magicbot.timed_state(duration=2.0, next_state="stop", first=True)
    def start(self):
        self.drivetrain.move(0.9, 0)

    @magicbot.state()
    def stop(self):
        self.drivetrain.stop()
