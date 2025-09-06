import commands2
from magicbot import feedback
import wpimath.geometry
import wpimath.units
import xrp


class XRPGyro(commands2.Subsystem):
    """Gyro class to handle the gyro functionality."""

    def __init__(self) -> None:
        """Initialize the gyro."""
        self.gyro = xrp.XRPGyro()

    def get_angles(self) -> tuple[float, float, float]:
        """Get the angles from the gyro."""
        return (self.get_x(), self.get_y(), self.get_z())

    def get_rotation2d(self) -> wpimath.geometry.Rotation2d:
        """Get the rotation2d from the gyro."""
        return self.gyro.getRotation2d()

    def get_x(self) -> float:
        return wpimath.units.radiansToDegrees(self.gyro.getAngleX())

    def get_y(self) -> float:
        return wpimath.units.radiansToDegrees(self.gyro.getAngleY())

    def get_z(self) -> float:
        return wpimath.units.radiansToDegrees(self.gyro.getAngleZ())
    
    def get_yaw(self) -> float:
        return self.get_z()

    def reset(self) -> None:
        """Reset the gyro."""
        self.gyro.reset()
