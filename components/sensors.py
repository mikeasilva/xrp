import magicbot
import xrp


class Accelerometer:
    def execute(self) -> None:
        pass

    def setup(self):
        self.gyro = xrp.XRPGyro()

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="X")
    def x(self) -> float:
        return self.gyro.getRateX()

    @magicbot.feedback(key="Y")
    def y(self) -> float:
        return self.gyro.getRateY()

    @magicbot.feedback(key="Z")
    def z(self) -> float:
        return self.gyro.getRateZ()


class Distance:
    """Distance sensor class to handle the distance sensor functionality."""

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        """Initialize the distance sensor."""
        self.unit = "in"
        self.distance_sensor = xrp.XRPRangefinder()

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def set_unit(self, unit: str) -> None:
        """Set the unit for distance measurement."""
        valid_units = ["inch", "in", "feet", "ft", "yard", "yd", "cm", "meter"]
        if unit not in valid_units:
            raise ValueError(f"Invalid unit. Valid units are: {valid_units}")
        self.unit = unit

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="sonar distance")
    def sonar_distance(self) -> float:
        """Get the distance from the sensor in various units (inches by default)."""
        # The distance from the sensor is in meters by default.
        # Convert to the requested unit.
        distance = self.distance_sensor.getDistance()
        if self.unit == "inch" or self.unit == "in" or self.unit == '"':
            distance = distance * 39.3701
        elif self.unit == "feet" or self.unit == "ft" or self.unit == "'":
            distance = distance * 3.28084
        elif self.unit == "yard" or self.unit == "yd":
            distance = distance * 1.09361
        elif self.unit == "cm":
            distance = distance * 100
        elif self.unit == "meter":
            return distance
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )
        return distance

    """
    @magicbot.feedback(key="Nearest Object")
    def get_sonar_distance_string(self) -> str:
        distance = int(round(self.get_distance(), 0))
        return f"{distance}{self.unit}"
    """

    @magicbot.feedback(key="unit")
    def get_unit(self) -> str:
        """Get the current unit for distance measurement."""
        return self.unit


class Gyro:
    def execute(self) -> None:
        pass

    def setup(self) -> None:
        self.gyro = xrp.XRPGyro()

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Pitch")
    def pitch(self) -> float:
        return self.gyro.getAngleY()

    @magicbot.feedback(key="Roll")
    def roll(self) -> float:
        return self.gyro.getAngleX()

    @magicbot.feedback(key="Yaw")
    def yaw(self) -> float:
        return self.gyro.getAngleZ()


class Reflectance:
    """Handles the reflectance (line) sensor functionality."""

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        """Initialize the sensor."""
        self.line_sensor = xrp.XRPReflectanceSensor()

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="left")
    def left_reflectance(self) -> float:
        """Returns the value from the left sensor."""
        return self.line_sensor.getLeftReflectanceValue()

    @magicbot.feedback(key="right")
    def right_reflectance(self) -> float:
        """Returns the value from the right sensor."""
        return self.line_sensor.getRightReflectanceValue()
