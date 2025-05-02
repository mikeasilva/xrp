import commands2
import wpilib.drive
import constants
import math
import wpilib
import wpimath
import xrp


class Drive(commands2.SubsystemBase):
    def __init__(self):
        super().__init__()
        self.left_motor = xrp.XRPMotor(constants.LEFT_MOTOR_CHANNEL)
        self.right_motor = xrp.XRPMotor(constants.RIGHT_MOTOR_CHANNEL)
        # Invert the right motor to match the left motor's direction
        self.right_motor.setInverted(True)

        # The XRP has onboard encoders that are hardcoded
        # to use DIO pins 4/5 and 6/7 for the left and right
        self.left_encoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.right_encoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )

        # And an onboard gyro (and you have to power on your XRP when it is on flat surface)
        self.gyro = xrp.XRPGyro()
        self.accelerometer = wpilib.BuiltInAccelerometer()
        self.reflectance_sensor = xrp.XRPReflectanceSensor()
        self.distance_sensor = xrp.XRPRangefinder()

        COUNTS_PER_REVOLUTION = (
            constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO
        )  # 585.0

        # Use inches as unit for encoder distances
        self.left_encoder.setDistancePerPulse(
            (math.pi * constants.WHEEL_DIAMETER_INCH) / COUNTS_PER_REVOLUTION
        )
        self.right_encoder.setDistancePerPulse(
            (math.pi * constants.WHEEL_DIAMETER_INCH) / COUNTS_PER_REVOLUTION
        )
        self.reset_encoders()
        self.reset_gyro()

        # Set up the differential drive controller and differential drive odometry
        self.drivetrain = wpilib.drive.DifferentialDrive(
            self.left_motor, self.right_motor
        )
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d.fromDegrees(self.get_gyro_angle_z()),
            self.get_left_distance_inch(),
            self.get_right_distance_inch(),
        )

        # Settings for the crash avoidance system
        self.crash_avoidance_enabled = True
        self.crash_avoidance_distance = constants.CRASH_AVOIDANCE_DISTANCE

    def tank_drive(self, left_speed, right_speed):
        # The crash avoidance system check
        forward_speed = 0
        if left_speed > 0 and right_speed > 0:
            forward_speed = 1
        if not self.at_risk_of_crashing(forward_speed):
            # If the robot is not at risk of crashing, drive normally
            self.left_motor.set(left_speed)
            self.right_motor.set(right_speed)

    def arcade_drive(self, fwd: float, rot: float) -> None:
        """
        Drives the robot using arcade controls.

        :param fwd: the commanded forward movement
        :param rot: the commanded rotation
        """
        # The crash avoidance system check
        if not self.at_risk_of_crashing(fwd):
            # If the robot is not at risk of crashing, drive normally
            self.drivetrain.arcadeDrive(fwd, rot)

    def at_risk_of_crashing(self, forward_speed=0) -> None:
        if self.crash_avoidance_enabled:
            return (
                self.get_distance_to_obstacle() - self.crash_avoidance_distance <= 0
                and forward_speed > 0
            )
        return False

    def set_crash_avoidance_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the crash avoidance system.

        :param enabled: True to enable, False to disable
        """
        self.crash_avoidance_enabled = enabled

    def stop(self) -> None:
        """
        Stop the drivetrain motors
        """
        self.drivetrain.arcadeDrive(0, 0)

    def tank_drive2(self, left: float, right: float) -> None:
        """
        Drives the robot using tank controls.

        :param left: the commanded left movement
        :param right: the commanded right movement
        """
        # The crash avoidance system check
        forward_speed = 0
        if left > 0 and right > 0:
            forward_speed = 1
        if not self.at_risk_of_crashing(forward_speed):
            # If the robot is not at risk of crashing, drive normally
            self.drivetrain.tankDrive(left, right)

    def reset_encoders(self) -> None:
        """Resets the drive encoders to currently read a position of 0."""
        self.left_encoder.reset()
        self.right_encoder.reset()

    def get_left_encoder_count(self) -> int:
        return self.left_encoder.get()

    def get_right_encoder_count(self) -> int:
        return self.right_encoder.get()

    def get_left_distance_inch(self) -> float:
        return -self.left_encoder.getDistance()

    def get_right_distance_inch(self) -> float:
        return -self.right_encoder.getDistance()

    def get_average_distance_inch(self) -> float:
        """Gets the average distance of the TWO encoders."""
        return (self.get_left_distance_inch() + self.get_right_distance_inch()) / 2.0

    def get_accel_x(self) -> float:
        """The acceleration in the X-axis.

        :returns: The acceleration of the XRP along the X-axis in Gs
        """
        return self.accelerometer.getX()

    def get_accel_y(self) -> float:
        """The acceleration in the Y-axis.

        :returns: The acceleration of the XRP along the Y-axis in Gs
        """
        return self.accelerometer.getY()

    def get_accel_z(self) -> float:
        """The acceleration in the Z-axis.

        :returns: The acceleration of the XRP along the Z-axis in Gs
        """
        return self.accelerometer.getZ()

    def get_gyro_angle_x(self) -> float:
        """Current angle of the XRP around the X-axis.

        :returns: The current angle of the XRP in degrees
        """
        return self.gyro.getAngleX()

    def get_gyro_angle_y(self) -> float:
        """Current angle of the XRP around the Y-axis.

        :returns: The current angle of the XRP in degrees
        """
        return self.gyro.getAngleY()

    def get_gyro_angle_z(self) -> float:
        """Current angle of the XRP around the Z-axis.

        :returns: The current angle of the XRP in degrees
        """
        return self.gyro.getAngleZ()

    def get_distance_to_obstacle(self, unit="inch") -> float:
        """Distance to obstacle in the front, as given by the distance sensor

        :returns: Distance in the requested unit.
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

    def reset_gyro(self) -> None:
        """Reset the gyro"""
        self.gyro.reset()

    def reset_odometry(
        self, pose: wpimath.geometry.Pose2d = wpimath.geometry.Pose2d()
    ) -> None:
        self.reset_gyro()
        self.reset_encoders()
        heading = wpimath.geometry.Rotation2d.fromDegrees(self.get_gyro_angle_z())
        self.odometry.resetPosition(
            heading, self.get_left_distance_inch(), self.get_right_distance_inch(), pose
        )

    def stop(self):
        self.tank_drive(0, 0)
