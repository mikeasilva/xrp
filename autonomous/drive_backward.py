import components
import magicbot


class DriveBackward(magicbot.AutonomousStateMachine):
    MODE_NAME = "Drive Backward"
    DEFAULT = False

    drivetrain: components.Drivetrain
    led: components.LED

    @magicbot.state(first=True)
    def led_on(self):
        self.led.on()
        self.next_state("start")

    @magicbot.timed_state(duration=2.0, next_state="stop")
    def start(self):
        self.drivetrain.move(-0.9, 0)

    @magicbot.state()
    def stop(self):
        self.led.off()
        self.drivetrain.stop()
        self.done()
