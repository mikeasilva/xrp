import magicbot
import xrp


class XRPServo:
    channel: int

    def setup(self):
        self.servo = xrp.XRPServo(self.channel)
        self._position = self.servo.getPosition()

    def execute(self):
        self.servo.setPosition(self.position)

    @magicbot.feedback(key="position")
    def get_position(self) -> float:
        return self.servo.getPosition()

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value) -> None:
        # Make sure the position is between 0 and 1
        self._position = max(0.0, min(1.0, value))
