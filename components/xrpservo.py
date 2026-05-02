import magicbot
import xrp


class XRPServo:
    channel: int
    position: float = 0.0

    def setup(self):
        self.servo = xrp.XRPServo(self.channel)
        self.position = self.servo.getPosition()

    def execute(self):
        self.servo.setPosition(self.position)

    @magicbot.feedback(key="position")
    def get_position(self) -> float:
        return self.servo.getPosition()
