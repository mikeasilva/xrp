import commands2
import constants
import xrp


class Arm(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()
        self.arm = xrp.XRPServo(constants.ARM_SERVO_CHANNEL)

    '''
    def _degrees_to_radians(self, degrees: float) -> float:
        """
        Convert degrees to radians.

        :param degrees: The angle in degrees.
        :return: The angle in radians.
        """
        return degrees * (math.pi / 180.0)

    def _radians_to_degrees(self, radians: float) -> float:
        """
        Convert radians to degrees.

        :param radians: The angle in radians.
        :return: The angle in degrees.
        """
        return radians * (180.0 / math.pi)

    def get_angle(self) -> float:
        """
        Get the current angle of the arm servo.

        :return: The current angle of the arm servo in degrees.
        """
        return self._radians_to_degrees(self.arm.getAngle())

    def set_angle(self, degrees: float) -> None:
        """
        Set the angle of the arm servo.

        param degrees: The angle to set the arm servo to, in degrees.
        The angle should be between 0 and 180 degrees.
        """
        # Set the angle of the arm servo
        self.arm.setAngle(self._degrees_to_radians(degrees))
    '''

    def get_position(self) -> float:
        return self.arm.getPosition()

    def set_position(self, degrees) -> None:
        self.arm.setPosition(degrees)
