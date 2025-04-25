import commands2
import wpimath.units
import xrp


class Gyro(commands2.Subsystem):
    """Gyro class to handle the gyro functionality."""

    def __init__(self) -> None:
        """Initialize the gyro."""
        self.gyro = xrp.XRPGyro()

    def calibrate(self) -> None:
        """Calibrate the gyro."""
        self.gyro.calibrate()

    def get_angles(self) -> tuple[float, float, float]:
        """Get the angles from the gyro."""
        return (self.get_x(), self.get_y(), self.get_z())

    def get_x(self) -> float:
        return wpimath.units.radiansToDegrees(self.gyro.getAngleX())

    def get_y(self) -> float:
        return wpimath.units.radiansToDegrees(self.gyro.getAngleY())

    def get_z(self) -> float:
        return wpimath.units.radiansToDegrees(self.gyro.getAngleZ())

    def reset(self) -> None:
        """Reset the gyro."""
        self.gyro.reset()
