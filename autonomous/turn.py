import components
import magicbot


class Turn(magicbot.AutonomousStateMachine):
    MODE_NAME = "Turn CW"
    DEFAULT = False

    drivetrain: components.Drivetrain
    led: components.LED

    @magicbot.state(first=True)
    def start(self):
        self.next_state("led_on")

    @magicbot.state()
    def led_on(self):
        self.led.turn_on()
        self.next_state("turn")

    @magicbot.timed_state(duration=2.0, next_state="finish")
    def turn(self):
        self.drivetrain.go(0, 1)

    @magicbot.state()
    def finish(self):
        self.drivetrain.stop()
        self.led.turn_off()
        self.done()
