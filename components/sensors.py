import magicbot
import xrp


class Accelerometer:
    xrp_gyro: xrp.XRPGyro

    def execute(self) -> None:
        pass

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="X")
    def x(self) -> float:
        return self.xrp_gyro.getRateX()

    @magicbot.feedback(key="Y")
    def y(self) -> float:
        return self.xrp_gyro.getRateY()

    @magicbot.feedback(key="Z")
    def z(self) -> float:
        return self.xrp_gyro.getRateZ()


class DistanceSensor:
    """Distance sensor class to handle the distance sensor functionality."""

    unit: str

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        """Initialize the distance sensor."""
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

    @magicbot.feedback(key="Sonar Distance")
    def sonar_distance(self) -> float:
        """Get the distance from the sensor in various units (inches by default)."""
        # The distance from the sensor is in meters by default.
        # Convert to the requested unit.
        distance = self.distance_sensor.getDistance()
        if (
            self.unit == "inch"
            or self.unit == "in"
            or self.unit == '"'
            or self.unit == "inches"
        ):
            distance = distance * 39.3701
        elif self.unit == "feet" or self.unit == "ft" or self.unit == "'":
            distance = distance * 3.28084
        elif self.unit == "yard" or self.unit == "yd" or self.unit == "yards":
            distance = distance * 1.09361
        elif self.unit == "cm":
            distance = distance * 100
        elif self.unit == "meter" or self.unit == "meters":
            return distance
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )
        return distance

    @magicbot.feedback(key="unit")
    def get_unit(self) -> str:
        """Get the current unit for distance measurement."""
        return self.unit


class Gyro:
    xrp_gyro: xrp.XRPGyro

    def execute(self) -> None:
        pass

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def reset(self) -> None:
        """Reset the accelerometer readings to zero."""
        self.xrp_gyro.reset()

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Pitch")
    def pitch(self) -> float:
        return self.xrp_gyro.getAngleY()

    @magicbot.feedback(key="Roll")
    def roll(self) -> float:
        return self.xrp_gyro.getAngleX()

    @magicbot.feedback(key="Yaw")
    def yaw(self) -> float:
        return self.xrp_gyro.getAngleZ()


class ReflectanceSensor:
    """Handles the reflectance (line) sensor functionality."""

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        """Initialize the sensor."""
        self.line_sensor = xrp.XRPReflectanceSensor()
        self.threshold = (
            0.5  # Value where the sensor detects a line (might need tuning)
        )

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

    @magicbot.feedback(key="Senses a Line")
    def senses_a_line(self) -> bool:
        """Returns True if either sensor detects a line."""
        return (
            self.left_reflectance() <= self.threshold
            or self.right_reflectance() <= self.threshold
        )

    def senses_a_line_on_the_left(self) -> bool:
        """Returns True if the left sensor detects a line."""
        return self.left_reflectance() <= self.threshold

    def senses_a_line_on_the_right(self) -> bool:
        """Returns True if the right sensor detects a line."""
        return self.right_reflectance() <= self.threshold
