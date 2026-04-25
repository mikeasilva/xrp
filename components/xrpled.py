import xrp
import wpilib


class XRPLed:
    blink_time: float

    def setup(self):
        self._blink_timer = wpilib.Timer()
        self.led = xrp.XRPOnBoardIO()
        self._mode = "on"
        self.led.setLed(True)
        print("LED Setup Done")

    def execute(self):
        if self._mode == "blink":
            if self._blink_timer.hasElapsed(self.blink_time):
                self.led.setLed(not self.led.getLed())
                self._blink_timer.reset()
        elif self._mode == "on":
            self.led.setLed(True)
        else:
            self.led.setLed(False)
        print(self.led.getLed())

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value):
        # Make sure the mode is always lower case
        self._mode = value.lower()
