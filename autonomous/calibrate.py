import components
import magicbot


class DriveBackward(magicbot.AutonomousStateMachine):
    MODE_NAME = "Calibrate"
    DEFAULT = False

    drivetrain: components.Drivetrain
    led: components.LED

    @magicbot.state(first=True)
    def led_on(self):
        self.smallest_max_speed = 1.0
        self.led.on()
        self.next_state("forward")

    @magicbot.timed_state(duration=10.0, next_state="backward")
    def forward(self):
        self.drivetrain.move(1, 0)
        left_speed, right_speed = self.drivetrain.get_speeds()
        self.smallest_max_speed = min(self.smallest_max_speed, abs(left_speed), abs(right_speed))

    @magicbot.timed_state(duration=10.0, next_state="stop")
    def backward(self):
        self.drivetrain.move(-1, 0)
        left_speed, right_speed = self.drivetrain.get_speeds()
        self.smallest_max_speed = min(self.smallest_max_speed, abs(left_speed), abs(right_speed))

    @magicbot.state()
    def stop(self):
        print(f"Smallest max speed: {self.smallest_max_speed}")
        self.led.off()
        self.drivetrain.stop()
        self.done()
