import xrp
import wpimath.units
import commands2


class DistanceSensor(commands2.Subsystem):
    """Distance sensor class to handle the distance sensor functionality."""

    def __init__(self) -> None:
        """Initialize the distance sensor."""
        self.distance_sensor = xrp.XRPRangefinder()

    def get_distance(self, unit="inch") -> float:
        """Get the distance from the sensor in various units (inches by default)."""
        # The distance from the sensor is in meters by default.
        # Convert to the requested unit.
        distance = self.distance_sensor.getDistance()
        if unit == "inch" or unit == "in":
            return distance * 39.3701
        elif unit == "cm":
            return distance * 100
        elif unit == "meter":
            return distance
        elif unit == "feet" or unit == "ft":
            return distance * 3.28084
        elif unit == "yard" or unit == "yd":
            return distance * 1.09361
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )


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
