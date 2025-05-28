import magicbot
import components


class AutonomousMode(magicbot.AutonomousStateMachine):
    MODE_NAME = "Automagic"
    DEFAULT = True

    drivetrain: components.Drivetrain

    @magicbot.timed_state(first=True, duration=2.0)
    def drive_forward(self):
        self.drivetrain.set_speed(0.9)

    def done(self):
        self.drivetrain.stop()
