import xrp
import magicbot


class Arm:
    servo: xrp.XRPServo
    current_angle = magicbot.tunable(0.0)
    target_angle = magicbot.tunable(0.0)
    is_not_moving = magicbot.tunable(True)

    def execute(self) -> None:
        if self.current_angle != self.target_angle:
            self.is_not_moving = False
            self.set_angle(self.target_angle)
        else:
            self.is_not_moving = True

    def setup(self) -> None:
        """Initialize the arm servo."""
        self.get_current_angle()

    def extend(self) -> None:
        """Extends the arm all the way down."""
        self.set_target_angle(0)

    def get_current_angle(self) -> float:
        """Get the current angle of the servo."""
        self.current_angle = self.servo.getAngle()
        return self.current_angle

    def lift(self, by: float = 0.1) -> None:
        """Lift the arm by a specified amount."""
        new_angle = min(180, self.get_current_angle() + by)
        self.set_target_angle(new_angle)

    def lower(self, by: float = 0.1) -> None:
        """Lower the arm by a specified amount."""
        new_angle = max(0, self.get_current_angle() - by)
        self.set_target_angle(new_angle)

    def retract(self) -> None:
        """Retract the arm all the way up."""
        self.set_target_angle(180)

    def set_angle(self, degrees: float) -> None:
        """Set the arm's angle."""
        self.current_angle = degrees
        self.servo.setAngle(degrees)

    def set_target_angle(self, degrees: float) -> None:
        """Set the target angle for the arm."""
        if self.is_not_moving:
            self.target_angle = degrees
