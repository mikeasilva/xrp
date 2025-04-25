import xrp
import wpimath.units
import commands2


class DistanceSensor(commands2.Subsystem):
    """Distance sensor class to handle the distance sensor functionality."""

    def __init__(self) -> None:
        """Initialize the distance sensor."""
        self.distance_sensor = xrp.XRPRangefinder()

    def get_distance(self) -> float:
        """Get the distance from the sensor."""
        return wpimath.units.metersToInches(self.distance_sensor.getDistance())


class LineSensor(commands2.Subsystem):
    """Handles the line sensor functionality."""

    def __init__(self) -> None:
        """Initialize the line sensor."""
        self.line_sensor = xrp.XRPReflectanceSensor()

    def get_left_sensor(self) -> float:
        """Returns the value from the left sensor."""
        return self.line_sensor.getLeftReflectanceValue()

    def get_right_sensor(self) -> float:
        """Returns the value from the right sensor."""
        return self.line_sensor.getRightReflectanceValue()
