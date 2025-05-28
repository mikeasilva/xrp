import wpilib
import magicbot
import xrp


class LED:
    io: xrp.XRPOnBoardIO
    enabled: bool
    blink_timer: wpilib.Timer
    blink_on_off_duration: magicbot.tunable

    def __init__(self):
        self.io = xrp.XRPOnBoardIO()
        self.blink_timer = wpilib.Timer()
        self.enabled = False
        self.blink_on_off_duration = 0.5

    def blink(self) -> None:
        """
        Blink the LED for a specified duration.
        """
        self.blink_timer.start()

        # How much time has passed?
        if self.blink_timer.get() >= self.blink_on_off_duration:
            # If the LED is on, turn it off and vice versa
            if self.enabled:
                self.turn_off()
            else:
                self.turn_on()
            # Reset the timer
            self.blink_timer.reset()

    def set_blink_duration(self, microseconds: float):
        self.blink_on_off_duration = microseconds

    def turn_off(self) -> None:
        """
        Turn the LED off.
        """
        self.enabled = False
        self.io.setLed(self.enabled)

    def turn_on(self) -> None:
        """
        Turn the LED on.
        """
        self.enabled = True
        self.io.setLed(self.enabled)

    def enable(self):
        self.turn_off()

    def execute(self):
        pass
