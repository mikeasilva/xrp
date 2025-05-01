import commands2
import xrp


class Arm(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()
        # Device number 4 maps to the physical Servo 1 port on the XRP
        self.armServo = xrp.XRPServo(4)

    def set_angle(self, degrees: float) -> None:
        self.armServo.setAngle(degrees)

    def get_angle(self) -> float:
        return self.armServo.getAngle()

    def extend_arm(self) -> None:
        self.set_angle(0)

    def retract_arm(self) -> None:
        self.set_angle(180)
