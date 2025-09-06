import commands2
import constants
import math
import wpilib.drive
import xrp


class XRPDrivetrain(commands2.Subsystem):
    def __init__(self, drive_mode: str = "arcade") -> None:
        """
        Initialize the drivetrain subsystem.

        :param drive_mode: the mode for driving the XRP robot, either 'arcade' or 'tank'
        """
        super().__init__()
        self.left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_CHANNEL)
        self.right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_CHANNEL)
        self.right_motor.setInverted(True)
        self.left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )
        self.reset_encoders()

        wheel_circumference = constants.WHEEL_DIAMETER_INCH * math.pi
        counts_per_wheel_revolution = (
            constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO
        )

        # And since we know the circumference of the wheel, we can calculate:
        distance_per_pulse = wheel_circumference / counts_per_wheel_revolution

        # We can tell the encoder to use distance per pulse
        # This changes the values returned by getDistance() to be in inches
        self.left_encoder.setDistancePerPulse(distance_per_pulse)
        self.right_encoder.setDistancePerPulse(distance_per_pulse)

        self.drivetrain = wpilib.drive.DifferentialDrive(
            self.left_motor, self.right_motor
        )

        self.drive_mode = drive_mode

    def arcadeDrive(self, fwd: float, rot: float) -> None:
        """
        Drives the robot using arcade controls.

        :param fwd: the commanded forward movement
        :param rot: the commanded rotation
        """
        self.drivetrain.arcadeDrive(-fwd, -rot)

    def drive(self, a: float, b: float) -> None:
        """
        Drive the robot using the specified drive mode.

        :param a: the commanded forward movement or left movement
        :param b: the commanded rotation or right movement
        """
        if self.drive_mode == "arcade":
            self.arcadeDrive(a, b)
        elif self.drive_mode == "tank":
            self.tankDrive(a, b)

    def feed(self) -> None:
        """
        Feed the robot forward.
        """
        self.drivetrain.feed()

    def get_distance_traveled(self) -> float:
        """
        Get the distance traveled by the robot.

        :return: the distance traveled in inches
        """
        return (
            self.left_encoder.getDistance() + self.right_encoder.getDistance()
        ) / 2.0

    def scale_distance(self, distance: float, units="in") -> float:
        """
        Scale a distance to the appropriate units.

        :param distance: the distance to scale
        :param units: the units to scale to, either 'in' or 'm'
        :return: the scaled distance
        """
        if units == "in":
            return distance
        elif units == "m":
            return distance * 0.0254
        else:
            raise ValueError("Units must be either 'in' or 'm'")
        
    def get_left_encoder_position(self, units="in") -> float:
        """
        Get the position of the left encoder.

        :return: the position of the left encoder in inches
        """
        return self.scale_distance(self.left_encoder.get(), units)

    def get_right_encoder_position(self, units="in") -> float:
        """
        Get the position of the right encoder.

        :return: the position of the right encoder in inches
        """
        return self.scale_distance(self.right_encoder.get(), units)

    def reset_encoders(self) -> None:
        """
        Reset the encoders to zero.
        """
        self.left_encoder.reset()
        self.right_encoder.reset()

    def safe(self, mode: bool = True) -> None:
        """
        Set the safety mode of the drivetrain.

        :param mode: True to enable safety, False to disable
        """
        self.drivetrain.setSafetyEnabled(mode)

    def set_drive_mode(self, mode: str) -> None:
        """
        Set the drive mode of the drivetrain.

        :param mode: the mode for driving the XRP robot, either 'arcade' or 'tank'
        """
        if mode not in ["arcade", "tank"]:
            raise ValueError("Drive mode must be either 'arcade' or 'tank'")
        self.drive_mode = mode

    def stop(self) -> None:
        """
        Stop the drivetrain motors
        """
        self.drivetrain.stopMotor()

    def tankDrive(self, left: float, right: float) -> None:
        """
        Drives the robot using tank controls.

        :param left: the commanded left movement
        :param right: the commanded right movement
        """
        self.drivetrain.tankDrive(-left, -right)
