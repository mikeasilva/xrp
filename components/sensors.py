import wpilib
import xrp


class Accelerometer:
    accelerometer: wpilib.BuiltInAccelerometer

    def execute(self) -> None:
        pass

    def get_x(self) -> float:
        """The acceleration in the X-axis.

        :returns: The acceleration of the XRP along the X-axis in Gs
        """
        return self.accelerometer.getX()

    def get_y(self) -> float:
        """The acceleration in the Y-axis.

        :returns: The acceleration of the XRP along the Y-axis in Gs
        """
        return self.accelerometer.getY()

    def get_z(self) -> float:
        """The acceleration in the Z-axis.

        :returns: The acceleration of the XRP along the Z-axis in Gs
        """
        return self.accelerometer.getZ()


class DistanceSensor:
    distance_sensor: xrp.XRPRangefinder

    def execute(self) -> None:
        pass

    def get_distance(self, unit="inch") -> float:
        """Distance to obstacle in the front, as given by the distance sensor

        :param unit: The unit to convert to. Can be 'inch', 'feet', 'yard', 'cm', or 'meter'
        :returns: The distance to the obstacle in the requested unit
        """
        distance = self.distance_sensor.getDistance()
        if unit == "inch" or unit == "in":
            return distance * 39.3701
        elif unit == "feet" or unit == "ft":
            return distance * 3.28084
        elif unit == "yard" or unit == "yd":
            return distance * 1.09361
        elif unit == "cm":
            return distance * 100
        elif unit == "meter":
            return distance
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )


class ReflectanceSensor:
    reflectance_sensor: xrp.XRPReflectanceSensor

    def execute(self) -> None:
        pass

    def get_left(self) -> float:
        return self.reflectance_sensor.getLeftReflectanceValue()

    def get_right(self) -> float:
        return self.reflectance_sensor.getRightReflectanceValue()
