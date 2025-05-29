import xrp
import magicbot


class Arm:
    servo: xrp.XRPServo
    servo_angle = magicbot.tunable(0)

    def execute(self) -> None:
        pass

    def extend(self) -> None:
        """Extends the arm all the way down."""
        self.set_angle(0)

    def get_angle(self) -> float:
        """Get the current angle of the servo."""
        return self.servo.getAngle()

    def lift(self, by: float = 0.1) -> None:
        """Lift the arm by a specified amount."""
        new_angle = max(180, self.get_angle() + by)
        self.set_angle(new_angle)

    def lower(self, by: float = 0.1) -> None:
        """Lower the arm by a specified amount."""
        new_angle = max(0, self.get_angle() - by)
        self.set_angle(new_angle)

    def retract(self) -> None:
        """Retract the arm all the way up."""
        self.set_angle(180)

    def set_angle(self, degrees: float) -> None:
        """Set the arm's angle."""
        self.servo_angle = degrees
        self.servo.setAngle(degrees)
