from .xrpgyro import XRPGyro
from .xrptankdrive import XRPTankDrive
import magicbot
import wpimath.kinematics
import wpimath.geometry


class Odometery:
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0
    left_distance: float = 0.0
    right_distance: float = 0.0
    gyro: XRPGyro
    tankdrive: XRPTankDrive

    def setup(self):
        self.pose = wpimath.geometry.Pose2d(0, 0, wpimath.geometry.Rotation2d(0))
        # Set up odometry
        self.pose = wpimath.geometry.Pose2d(0, 0, wpimath.geometry.Rotation2d(0))
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d(self.gyro.angle),
            self.left_distance,
            self.right_distance,
            self.pose,
        )

        # Set up chassis speed
        self.chassis_speed = wpimath.kinematics.ChassisSpeeds(
            self.linear_velocity, 0, self.angular_velocity
        )

    def execute(self):
        # Update the odometry and pose estimation
        self.left_distance = self.tankdrive.left_encoder.getDistance()
        self.right_distance = self.tankdrive.right_encoder.getDistance()
        ## Update the odometry with the current gyro rate and encoder distances
        self.odometry.update(
            wpimath.geometry.Rotation2d(self.gyro.angle),
            self.left_distance,
            self.right_distance,
        )
        self.pose = self.odometry.getPose()

        # Update the chassis speed based on the current encoder rates and gyro rate
        ## Average the left and right encoder rates for the linear velocity
        linear_velocity = (
            self.tankdrive.right_encoder.getRate()
            - self.tankdrive.left_encoder.getRate()
        ) / 2
        ## Apply a filter to the linear velocity
        if abs(linear_velocity) < 0.001:
            linear_velocity = 0.0
        self.linear_velocity = linear_velocity
        ## The angular velocity is the rate of change of the gyro angle
        angular_velocity = self.gyro.get_rate()
        ## Apply a filter to the angular velocity
        if abs(angular_velocity) < 0.001:
            angular_velocity = 0.0
        self.angular_velocity = angular_velocity
        ## Update the chassis speed
        self.chassis_speed = wpimath.kinematics.ChassisSpeeds(
            self.linear_velocity, 0, self.angular_velocity
        )

    @magicbot.feedback
    def distance(self) -> float:
        return (self.right_distance + self.left_distance) / 2

    @magicbot.feedback(key="linear velocity")
    def get_linear_velocity(self) -> float:
        return self.linear_velocity

    @magicbot.feedback(key="angular velocity")
    def get_angular_velocity(self) -> float:
        return self.angular_velocity

    @magicbot.feedback(key="pose x")
    def get_pose_x(self) -> float:
        return self.pose.X()

    @magicbot.feedback(key="pose y")
    def get_pose_y(self) -> float:
        return self.pose.Y()
