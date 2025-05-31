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
    distances = [0]

    def execute(self) -> None:
        self.distances.append(self.xrp_distance_sensor.getDistance())
        if len(self.distances) > 20:
            self.distances.pop(0)

    def get_distance(self, unit="inch", precision=1) -> float:
        """Distance to obstacle in the front, as given by the distance sensor

        :param unit: The unit to convert to. Can be 'inch', 'feet', 'yard', 'cm', or 'meter'
        :returns: The distance to the obstacle in the requested unit
        """

        distance = sum(self.distances) / len(self.distances)
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

    def execute(self) -> None:
        pass

    def get_left(self) -> float:
        return self.xrp_reflectance_sensor.getLeftReflectanceValue()

    def get_right(self) -> float:
        return self.xrp_reflectance_sensor.getRightReflectanceValue()
