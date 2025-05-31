import magicbot
import wpilib
import xrp


class Accelerometer:
    xrp_accelerometer: wpilib.BuiltInAccelerometer

    def execute(self) -> None:
        pass

    def get_x(self) -> float:
        """The acceleration in the X-axis.

        :returns: The acceleration of the XRP along the X-axis in Gs
        """
        return self.xrp_accelerometer.getX()

    def get_y(self) -> float:
        """The acceleration in the Y-axis.

        :returns: The acceleration of the XRP along the Y-axis in Gs
        """
        return self.xrp_accelerometer.getY()

    def get_z(self) -> float:
        """The acceleration in the Z-axis.

        :returns: The acceleration of the XRP along the Z-axis in Gs
        """
        return self.xrp_accelerometer.getZ()


class DistanceSensor:
    xrp_distance_sensor: xrp.XRPRangefinder
    distances = []
    n_values = 20

    def execute(self) -> None:
        """Collects the distance from the distance sensor and stores it in a list."""
        self.distances.append(self.xrp_distance_sensor.getDistance())
        if len(self.distances) > self.n_values:
            self.distances.pop(0)

    def get_distance(self, unit="inch", precision=1) -> float:
        """Distance to obstacle in the front, as given by the distance sensor

        :param unit: The unit to convert to. Can be 'inch', 'feet', 'yard', 'cm', or 'meter'
        :returns: The distance to the obstacle in the requested unit
        """

        distance = average(self.distances)
        if unit == "inch" or unit == "in":
            return round(distance * 39.3701, precision)
        elif unit == "feet" or unit == "ft":
            return round(distance * 3.28084, precision)
        elif unit == "yard" or unit == "yd":
            return round(distance * 1.09361, precision)
        elif unit == "cm":
            return round(distance * 100, precision)
        elif unit == "meter":
            return round(distance, precision)
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )


class ReflectanceSensor:
    xrp_reflectance_sensor: xrp.XRPReflectanceSensor
    left_values = []
    right_values = []
    n_values = 10  # Number of values to keep in the list

    def execute(self) -> None:
        """Collects the reflectance values from the sensors and stores them in lists."""
        self.left_values.append(self.get_raw_left())
        self.right_values.append(self.get_raw_right())

        if len(self.left_values) > self.n_values:
            self.left_values.pop(0)

        if len(self.right_values) > self.n_values:
            self.right_values.pop(0)

    def get_left(self) -> float:
        """Get the average left reflectance value."""
        return round(average(self.left_values), 2)

    def get_right(self) -> float:
        """Get the average right reflectance value."""
        return round(average(self.right_values), 2)

    def get_raw_right(self) -> float:
        """Get the raw right reflectance value."""
        return self.xrp_reflectance_sensor.getRightReflectanceValue()

    def get_raw_left(self) -> float:
        """Get the raw left reflectance value."""
        return self.xrp_reflectance_sensor.getLeftReflectanceValue()


def average(values: list[float]) -> float:
    """Calculate the average of a list of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)
