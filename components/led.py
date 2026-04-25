import xrp
import wpilib


class LED:
    blink_time: float

    def setup(self):
        self._blink_timer = wpilib.Timer()
        self._blink_timer.start()
        self._led = xrp.XRPOnBoardIO()
        self._mode = "off"

    def execute(self):
        if self._mode == "blink":
            if self._blink_timer.hasElapsed(self.blink_time):
                self._led.setLed(not self._led.getLed())
                self._blink_timer.reset()
        elif self._mode == "on":
            self._led.setLed(True)
        else:
            self._led.setLed(False)

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value):
        # Make sure the mode is always lower case
        self._mode = value.lower()
