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
        self.set_track_minimum(False)
        self.reset_minimum()

    def execute(self):
        if self.track_minimum:
            self.left_motor.get()
            self.minimum = min(
                self.minimum, abs(self.left_motor.get()), abs(self.right_motor.get())
            )
        pass

    def go(self, left_stick: float, right_stick: float):
        if self.mode == "tank":
            self.drive.tankDrive(left_stick, right_stick)
        else:
            self.speed = left_stick
            self.rotation = right_stick
            if self.mode == "arcade":
                self.drive.arcadeDrive(self.speed, self.rotation, squareInputs=True)
            else:
                self.drive.curvatureDrive(
                    self.speed, self.rotation, allowTurnInPlace=True
                )

    def stop(self):
        self.speed = 0.0
        self.drive.stopMotor()

    def get_minimum(self) -> float:
        """Get the minimum speed recorded."""
        return self.minimum

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

        :param mode: The drive mode to set, either "arcade", "curvature" or "tank".
        """
        if mode not in ["arcade", "curvature", "tank"]:
            raise ValueError("Invalid drive mode. Use 'arcade', 'curvature' or 'tank'.")
        self.mode = mode

    def reset_minimum(self):
        """
        Reset the minimum speed to a high value.
        This is useful when starting a new calibration or measurement.
        """
        self.minimum = 999.0

    def set_track_minimum(self, track: bool):
        """
        Set whether to track the minimum speed.

        :param track: If True, track the minimum speed.
        """
        self.track_minimum = track
