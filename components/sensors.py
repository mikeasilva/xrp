from magicbot import feedback
import xrp


class DistanceSensor:
    """Distance sensor class to handle the distance sensor functionality."""

    UNIT = "inch"

    def setup(self) -> None:
        """Initialize the distance sensor."""
        self.distance_sensor = xrp.XRPRangefinder()

    def execute(self) -> None:
        pass

    @feedback(key="distance")
    def get_distance(self) -> float:
        """Get the distance from the sensor in various units (inches by default)."""
        # The distance from the sensor is in meters by default.
        # Convert to the requested unit.
        distance = self.distance_sensor.getDistance()
        if self.UNIT == "inch" or self.UNIT == "in":
            return distance * 39.3701
        elif self.UNIT == "feet" or self.UNIT == "ft":
            return distance * 3.28084
        elif self.UNIT == "yard" or self.UNIT == "yd":
            return distance * 1.09361
        elif self.UNIT == "cm":
            return distance * 100
        elif self.UNIT == "meter":
            return distance
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )

    @feedback(key="unit")
    def get_unit(self) -> str:
        """Get the current unit for distance measurement."""
        return self.UNIT

    def set_unit(self, unit: str) -> None:
        """Set the unit for distance measurement."""
        valid_units = ["inch", "in", "feet", "ft", "yard", "yd", "cm", "meter"]
        if unit not in valid_units:
            raise ValueError(f"Invalid unit. Valid units are: {valid_units}")
        self.UNIT = unit


class LineSensor:
    """Handles the line sensor functionality."""

    def setup(self) -> None:
        """Initialize the line sensor."""
        self.line_sensor = xrp.XRPReflectanceSensor()

    def execute(self) -> None:
        pass

    @feedback(key="left")
    def get_left_sensor(self) -> float:
        """Returns the value from the left sensor."""
        return self.line_sensor.getLeftReflectanceValue()

    @feedback(key="right")
    def get_right_sensor(self) -> float:
        """Returns the value from the right sensor."""
        return self.line_sensor.getRightReflectanceValue()
