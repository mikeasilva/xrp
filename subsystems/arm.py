import commands2
import constants
import xrp


class Arm(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()
        # Device number 4 maps to the physical Servo 1 port on the XRP
        self.servo = xrp.XRPServo(constants.ARM_SERVO_CHANNEL)

    def extend(self) -> None:
        """Extends the arm all the way down."""
        self.set_angle(0)

    def get_angle(self) -> float:
        """Get the current angle of the servo."""
        return self.servo.getAngle()

    def retract(self) -> None:
        """Retract the arm all the way up."""
        self.set_angle(180)

    def set_angle(self, degrees: float) -> None:
        """Set the arm's angle."""
        self.servo.setAngle(degrees)
