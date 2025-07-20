import magicbot
from magicbot import feedback
import wpilib.drive
import xrp


class TankDrive:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor

    def setup(self):
        self.speed = 0.0
        self.rotation = 0.0
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.mode = "arcade"  # Default to arcade drive

    def execute(self):
        pass

    def go(self, left_stick: float, right_stick: float):
        if self.mode == "arcade":
            self.speed = left_stick
            self.rotation = right_stick
            self.drive.arcadeDrive(self.speed, self.rotation, squareInputs=True)
        else:
            self.drive.tankDrive(left_stick, right_stick)

    def stop(self):
        self.speed = 0.0
        self.drive.stopMotor()

    @feedback(key="Mode")
    def get_mode(self) -> str:
        """Get the current drive mode."""
        return self.mode

    @feedback(key="Speed")
    def get_speed(self) -> float:
        """Get the speed passed into the drive."""
        return self.speed

    @feedback(key="Rotation")
    def get_rotation(self) -> float:
        """Get the rotation passed into the drive."""
        return self.rotation

    def set_mode(self, mode: str):
        """
        Set the drive mode.

        :param mode: The drive mode to set, either "arcade" or "tank".
        """
        if mode not in ["arcade", "tank"]:
            raise ValueError("Invalid drive mode. Use 'arcade' or 'tank'.")
        self.mode = mode
