import magicbot
import xrp
import wpimath.units as units


class XRPRangefinder:
    # Check if they want raw or filtered distance values
    distance_mode: str = "filtered"  # "raw" or "filtered"

    def setup(self):
        self.sensor = xrp.XRPRangefinder()
        self._raw_distance = 0.0
        self._unit = "in"
        if self.distance_mode not in ["raw", "filtered"]:
            raise ValueError("Invalid distance mode. Must be 'raw' or 'filtered'.")

    def execute(self):
        self._raw_distance = self.sensor.getDistance()

    @property
    def distance(self):
        if self.unit == "m":
            if self.distance_mode == "raw":
                return self._raw_distance
            else:
                return round(self._raw_distance, 2)
        elif self.unit == "cm":
            if self.distance_mode == "raw":
                return self._raw_distance * 100
            else:
                return round(self._raw_distance * 100, 2)
        elif self.unit == "in":
            if self.distance_mode == "raw":
                return units.metersToInches(self._raw_distance)
            else:
                return round(units.metersToInches(self._raw_distance), 2)
        elif self.unit == "ft":
            if self.distance_mode == "raw":
                return units.metersToFeet(self._raw_distance)
            else:
                return round(units.metersToFeet(self._raw_distance), 2)
        elif self.unit == "yd":
            if self.distance_mode == "raw":
                return units.metersToFeet(self._raw_distance) / 3
            else:
                return round(units.metersToFeet(self._raw_distance) / 3, 2)

    @magicbot.feedback(key="distance")
    def _get_distance(self) -> float | None:
        return self.distance

    @property
    def unit(self):
        return self._unit

    @magicbot.feedback(key="unit")
    def _get_unit(self) -> str:
        return self.unit

    @unit.setter
    def unit(self, value):
        # Normalize the input
        value = value.lower()
        # Handle common variations of units
        if value in ["inches", "inch", '"']:
            value = "in"
        elif value in ["feet", "foot", "'"]:
            value = "ft"
        elif value in ["yards", "yard", "yrd"]:
            value = "yd"
        elif value in ["centimeters", "centimeter"]:
            value = "cm"
        elif value in ["meters", "meter"]:
            value = "m"
        # Check for valid unit
        if value not in ["in", "ft", "yd", "cm", "m"]:
            raise ValueError("Invalid unit. Must be 'in', 'ft', 'yd', 'cm', or 'm'.")
        self._unit = value


class XRPReflectanceSensor:
    threshold: float = 0.5
    line_on_left = False
    line_on_right = False

    def setup(self):
        self.sensor = xrp.XRPReflectanceSensor()
        self._raw_left = 0.0
        self._raw_right = 0.0

    def execute(self):
        self._raw_left = self.sensor.getLeftReflectanceValue()
        self._raw_right = self.sensor.getRightReflectanceValue()
        self.line_on_left = self._raw_left <= self.threshold
        self.line_on_right = self._raw_right <= self.threshold

    @magicbot.feedback(key="left reflectance")
    def _get_left_reflectance(self) -> float:
        return self._raw_left

    @magicbot.feedback(key="right reflectance")
    def _get_right_reflectance(self) -> float:
        return self._raw_right

    @magicbot.feedback(key="line on left")
    def _get_line_on_left(self) -> bool:
        return self.line_on_left

    @magicbot.feedback(key="line on right")
    def _get_line_on_right(self) -> bool:
        return self.line_on_right
