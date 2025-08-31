import components
import magicbot


class DriveForward(magicbot.AutonomousStateMachine):
    MODE_NAME = "Drive Forward"
    DEFAULT = True

    drivetrain: components.Drivetrain
    led: components.LED

    @magicbot.state(first=True)
    def start(self):
        self.next_state("led_on")

    @magicbot.state()
    def led_on(self):
        self.led.turn_on()
        self.next_state("drive_forward")

    @magicbot.timed_state(duration=1.0, next_state="finish")
    def drive_forward(self):
        self.drivetrain.go(1, 0)

    @magicbot.state()
    def finish(self):
        self.drivetrain.stop()
        self.led.turn_off()
        self.done()
