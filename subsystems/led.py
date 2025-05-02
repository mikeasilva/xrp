import commands2
import constants
import wpilib
import xrp


class LED(commands2.Subsystem):
    def __init__(self) -> None:
        """
        Initialize the LED subsystem.
        """
        super().__init__()
        self.io = xrp.XRPOnBoardIO()
        self.led_state = False
        self.io.setLed(self.led_state)
        self.blink_timer = wpilib.Timer()
        self.blink_on_off_duration = constants.LED_BLINK_DURATION_IN_SECONDS

    def blink(self) -> None:
        """
        Blink the LED for a specified duration.
        """
        self.blink_timer.start()

        # How much time has passed?
        time = self.blink_timer.get()
        if time >= self.blink_on_off_duration:
            # If the LED is on, turn it off and vice versa
            if self.led_state:
                self.off()
            else:
                self.on()
            # Reset the timer
            self.blink_timer.reset()

    def off(self) -> None:
        """
        Turn the LED off.
        """
        self.led_state = False
        self.io.setLed(self.led_state)

    def on(self) -> None:
        """
        Turn the LED on.
        """
        self.led_state = True
        self.io.setLed(self.led_state)
