import xrp
import wpilib


class LED:
    def setup(self) -> None:
        self.xrp_led = xrp.XRPOnBoardIO()
        self.blink_timer = wpilib.Timer()
        self.led_is_on = False
        self.turn_off()

    def execute(self):
        pass

    def blink(self, duration: float = 0.5) -> None:
        """
        Blink the LED for a specified duration.
        """
        self.blink_timer.start()

        # How much time has passed?
        time = self.blink_timer.get()
        if time >= duration:
            # If the LED is on, turn it off and vice versa
            if self.led_is_on:
                self.turn_off()
            else:
                self.turn_on()
            # Reset the timer
            self.blink_timer.reset()

    def set_led(self, state: bool) -> None:
        """
        Set the LED state directly.
        """
        self.led_is_on = state
        self.xrp_led.setLed(state)

    def turn_off(self) -> None:
        """
        Turn the LED off.
        """
        self.set_led(False)

    def turn_on(self) -> None:
        """
        Turn the LED on.
        """
        self.set_led(True)
