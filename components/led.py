import constants
import xrp
import wpilib


class LED:
    xrp_io: xrp.XRPOnBoardIO

    def setup(self) -> None:
        self.led_state = False
        self.xrp_io.setLed(self.led_state)
        self.blink_timer = wpilib.Timer()
        self.blink_on_off_duration = constants.LED_BLINK_DURATION_IN_SECONDS

    def execute(self) -> None:
        pass

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
        self.xrp_io.setLed(self.led_state)

    def on(self) -> None:
        """
        Turn the LED on.
        """
        self.led_state = True
        self.xrp_io.setLed(self.led_state)

    def get_blink_duration(self) -> float:
        """
        Get the duration for the LED blink on/off cycle.
        """
        return self.blink_on_off_duration

    def set_blink_duration(self, duration: float) -> None:
        """
        Set the duration for the LED blink on/off cycle.
        """
        self.blink_on_off_duration = duration
        self.blink_timer.reset()
