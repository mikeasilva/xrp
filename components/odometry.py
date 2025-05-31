import magicbot
import math
import wpilib
import wpimath.geometry
import wpimath.kinematics
import xrp


class Odometry:
    left_encoder: wpilib.Encoder
    right_encoder: wpilib.Encoder
    gyro: xrp.XRPGyro

    heading = magicbot.tunable(0.0)
    left_encoder_distance = magicbot.tunable(0.0)
    right_encoder_distance = magicbot.tunable(0.0)
    headings = []

    def setup(self) -> None:
        self.reset_gyro()
        self.reset_encoders()
        self.odometry = wpimath.kinematics._kinematics.DifferentialDriveOdometry(
            gyroAngle=wpimath.geometry.Rotation2d.fromDegrees(self.get_gyro_angle_z()),
            leftDistance=self.get_left_distance(),
            rightDistance=self.get_right_distance(),
        )

    def execute(self) -> None:
        self.left_encoder_distance = self.get_left_distance()
        self.right_encoder_distance = self.get_right_distance()
        self.headings.append(round(self.get_gyro_angle(), 0))
        if len(self.headings) > 10:
            self.headings.pop(0)
        self.heading = sum(self.headings) / len(self.headings)

    def get_left_distance(self) -> float:
        """
        Get the distance traveled by the left encoder.
        """
        return self.left_encoder.getDistance()

    def get_right_distance(self) -> float:
        """
        Get the distance traveled by the right encoder.
        """
        return self.right_encoder.getDistance()

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

    '''
    def get_heading(self) -> wpimath.geometry.Rotation2d:
        """Current actual angle the XRP is currently facing."""
        return self.get_pose().rotation()
    '''
    def get_heading(self) -> float:
        return round(self.heading, 0)

    def get_left_encoder_count(self) -> int:
        return self.left_encoder.get()

    def get_location(self):
        return self.get_pose().translation()

    def get_pose(self) -> wpimath.geometry.Pose2d:
        """Get the current pose of the robot.
        :returns: The current pose of the robot in the field frame
        """
        return self.odometry.getPose()

    def get_right_encoder_count(self) -> int:
        return self.right_encoder.get()

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
            heading, self.get_left_distance(), self.get_right_distance(), pose
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
