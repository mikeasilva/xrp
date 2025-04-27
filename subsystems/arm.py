import commands2
import xrp


class Arm(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()
        # Device number 4 maps to the physical Servo 1 port on the XRP
        self.armServo = xrp.XRPServo(4)

    def setAngle(self, degrees: float):
        self.armServo.setAngle(degrees)