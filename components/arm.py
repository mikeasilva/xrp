from magicbot import feedback
import xrp


class Arm:
    servo_channel: int

    def setup(self) -> None:
        self.arm = xrp.XRPServo(self.servo_channel)

    def execute(self) -> None:
        pass

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def set_position(self, degrees) -> None:
        self.arm.setPosition(degrees)

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @feedback(key="position")
    def get_position(self) -> float:
        return self.arm.getPosition()
