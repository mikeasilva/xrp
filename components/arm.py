from enum import Enum
import xrp
from magicbot import feedback


class ArmState(Enum):
    NOT_MOVING = 0
    RAISING = 1
    LOWERING = 2


class Arm:
    arm_servo: xrp.XRPServo

    def execute(self) -> None:
        if self.get_current_angle() == self.target_angle:
            self.state = ArmState.NOT_MOVING

        if self.state in [ArmState.RAISING, ArmState.LOWERING]:
            self.set_angle(self.target_angle)

    @feedback(key="Current Arm Angle")
    def get_current_angle(self) -> float:
        """Get the current angle of the servo."""
        return self.arm_servo.getAngle()

    @feedback(key="Arm State")
    def get_state(self) -> str:
        """Get the current state of the arm."""
        return self.state.name

    @feedback(key="Target Arm Angle")
    def get_target_angle(self) -> float:
        """Get the target angle of the servo."""
        return self.target_angle

    def lift(self, by: float = 0.1) -> None:
        """Lift the arm by a specified amount."""
        self.set_target_angle(min(180, self.get_current_angle() + by))

    def lower(self, by: float = 0.1) -> None:
        """Lower the arm by a specified amount."""
        self.set_target_angle(max(0, self.get_current_angle() - by))

    def setup(self) -> None:
        """Initialize the arm servo."""
        self.state = ArmState.NOT_MOVING
        self.target_angle = self.current_angle = self.get_current_angle()

    def set_angle(self, degrees: float) -> None:
        """Set the arm's angle."""
        # self.current_angle = degrees
        self.arm_servo.setAngle(degrees)

    def set_target_angle(self, degrees: float) -> None:
        """Set the target angle for the arm."""
        if self.state == ArmState.NOT_MOVING:
            if degrees > self.current_angle:
                self.state = ArmState.RAISING
            elif degrees < self.current_angle:
                self.state = ArmState.LOWERING
            self.target_angle = degrees
