import xrp
import wpilib


class XRPLed:
    blink_time: float

    def setup(self) -> None:
        self._timer = wpilib.Timer()
        self._led = xrp.XRPOnBoardIO()
        self._mode = "on"
        self._led.setLed(True)
        self._timer.start()

    def execute(self) -> None:
        if self.mode == "blink":
            if self._timer.hasElapsed(self.blink_time):
                self._led.setLed(not self._led.getLed())
                self._timer.reset()
        elif self.mode == "on":
            self._led.setLed(True)
        else:
            self._led.setLed(False)

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value) -> None:
        # Make sure the mode is always lower case
        self._mode = value.lower()
