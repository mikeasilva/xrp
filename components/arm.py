import constants
from magicbot import feedback
import xrp


class Arm:
    def setup(self) -> None:
        self.arm = xrp.XRPServo(constants.ARM_SERVO_CHANNEL)

    def execute(self) -> None:
        pass

    @feedback(key="position")
    def get_position(self) -> float:
        return self.arm.getPosition()

    def set_position(self, degrees) -> None:
        self.arm.setPosition(degrees)
