import commands2
import wpilib.drive
import constants
import math
import wpilib
import wpimath
import xrp


class XRPDrive(commands2.SubsystemBase):
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
        self.drivetrain.setSafetyEnabled(False)  # Disable safety checks
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d.fromDegrees(self.get_gyro_angle_z()),
            self.get_left_distance_inch(),
            self.get_right_distance_inch(),
        )

        # Settings for the crash avoidance system
        self.crash_avoidance_enabled = True
        self.crash_avoidance_distance = constants.CRASH_AVOIDANCE_DISTANCE

    def arcade_drive(self, forward: float, rotation: float) -> None:
        """
        Drives the robot using arcade controls.

        :param forward: the commanded forward movement
        :param rotation: the commanded rotation
        """
        # The crash avoidance system check
        if not self.at_risk_of_crashing(forward):
            # If the robot is not at risk of crashing, drive normally
            self.drivetrain.arcadeDrive(forward, rotation)

    def at_risk_of_crashing(self, forward_speed=0) -> bool:
        """
        Checks if the robot is at risk of crashing into an obstacle.

        :param forward_speed: The forward speed of the robot
        """

        if forward_speed < 0 or not self.crash_avoidance_enabled:
            return False
        # Crash avoidance system is enabled, check distance to obstacle
        # and if the robot is moving forward. If the distance to the obstacle is less than the
        # crash avoidance distance, return True.
        return (
            self.get_distance_to_obstacle() - self.crash_avoidance_distance <= 0
            and forward_speed > 0
        )

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

    def get_average_distance_inch(self) -> float:
        """Gets the average distance of the two encoders."""
        return (self.get_left_distance_inch() + self.get_right_distance_inch()) / 2.0

    def get_distance_to_obstacle(self, unit="inch") -> float:
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

    def get_gyro_angle(self, units: str = "degrees") -> float:
        """Current actual angle the XRP is currently facing.

        :param units: The unit to convert to. Can be 'degrees' or 'radians'
        :returns: The current angle of the XRP in degrees
        """
        return self._return_gyro(self.gyro.getAngle(), units)

    def get_gyro_angle_x(self, units="degrees") -> float:
        """Current angle of the XRP around the X-axis.

        :param units: The unit to convert to. Can be 'degrees' or 'radians'
        :returns: The current angle of the XRP in degrees
        """
        return self._return_gyro(self.gyro.getAngleX(), units)

    def get_gyro_angle_y(self, units: str = "degrees") -> float:
        """Current angle of the XRP around the Y-axis.

        :param units: The unit to convert to. Can be 'degrees' or 'radians'
        :returns: The current angle of the XRP in degrees or radians
        """
        return self._return_gyro(self.gyro.getAngleY(), units)

    def get_gyro_angle_z(self, units: str = "degrees") -> float:
        """Current angle of the XRP around the Z-axis.

        :param units: The unit to convert to. Can be 'degrees' or 'radians'
        :returns: The current angle of the XRP in degrees or radians
        """
        return self._return_gyro(self.gyro.getAngleZ(), units)

    def get_heading(self) -> wpimath.geometry.Rotation2d:
        """Current actual angle the XRP is currently facing."""
        return self.get_pose().rotation()

    def get_left_distance_inch(self) -> float:
        return -self.left_encoder.getDistance()

    def get_left_encoder_count(self) -> int:
        return self.left_encoder.get()

    def get_location(self):
        return self.get_pose().translation()

    def get_pose(self) -> wpimath.geometry.Pose2d:
        """Get the current pose of the robot.
        :returns: The current pose of the robot in the field frame
        """
        """
        # Update the odometry with the current gyro angle and encoder distances
        return self.odometry.update(
            wpimath.geometry.Rotation2d.fromDegrees(self.get_gyro_angle_z()),
            self.get_left_distance_inch(),
            self.get_right_distance_inch(),
        )
        """
        return self.odometry.getPose()

    def get_right_distance_inch(self) -> float:
        return -self.right_encoder.getDistance()

    def get_right_encoder_count(self) -> int:
        return self.right_encoder.get()

    def periodic(self) -> None:
        pose = self.get_pose()
        wpilib.SmartDashboard.putNumber("x", pose.x)
        wpilib.SmartDashboard.putNumber("y", pose.y)
        wpilib.SmartDashboard.putNumber("z-heading", pose.rotation().degrees())
        wpilib.SmartDashboard.putNumber(
            "distance-to-obstacle", self.get_distance_to_obstacle()
        )
        wpilib.SmartDashboard.putNumber(
            "left-reflect", self.reflectance_sensor.getLeftReflectanceValue()
        )
        wpilib.SmartDashboard.putNumber(
            "right-reflect", self.reflectance_sensor.getRightReflectanceValue()
        )

    def reset_encoders(self) -> None:
        """Resets the drive encoders to currently read a position of 0."""
        self.left_encoder.reset()
        self.right_encoder.reset()

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

    def _return_gyro(self, angle: float, units: str = "degrees") -> float:
        """Convert the angle to the requested unit.

        :param angle: The angle in radians
        :param units: The unit to convert to. Can be 'degrees' or 'radians'
        :returns: The angle in the requested unit
        """
        # Ensure the units are lowercase for consistency
        units = units.lower()
        if units == "degrees":
            return angle * (180 / math.pi)
        elif units == "radians":
            return angle
        raise ValueError("Invalid units. Use 'degrees' or 'radians'.")

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
        self.tank_drive(0, 0)

    def tank_drive(self, left_speed, right_speed):
        """
        Drives the robot using tank controls.

        :param left_speed: the speed of the left motor
        :param right_speed: the speed of the right motor
        """
        # The crash avoidance system check
        forward_speed = 0
        if left_speed > 0 and right_speed > 0:
            forward_speed = 1
        if not self.at_risk_of_crashing(forward_speed):
            # If the robot is not at risk of crashing, drive normally
            self.left_motor.set(left_speed)
            self.right_motor.set(right_speed)
