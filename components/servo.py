import magicbot
import xrp


class Servo:
    channel: int

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        self.servo = xrp.XRPServo(self.channel)

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def set_position(self, degrees) -> None:
        self.servo.setPosition(degrees)

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Position")
    def get_position(self) -> float:
        return self.servo.getPosition()
