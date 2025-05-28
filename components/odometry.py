import wpilib
import wpimath
import math
import xrp
import magicbot
import components
import constants


class Odometry:
    kinematics: wpimath.kinematics.DifferentialDriveKinematics
    gyro: xrp.XRPGyro
    left_encoder: components.XRPEncoder
    right_encoder: components.XRPEncoder
    # left_distance = ntproperty('/left distance/', 0)
    # right_distance = ntproperty('/right distance/', 0)

    def get_angle(self):
        return self.gyro.getAngle()

    def setup(self):
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpilib.geometry.Rotation2d(math.radians(self.getAngle()))
        )
        self.left_encoder = components.XRPEncoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.right_encoder = components.XRPEncoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )

    def get_pose(self) -> wpimath.geometry.Pose2d:
        return self.odometry.getPose()

    @magicbot.feedback
    def get_pose_string(self) -> str:
        pose = self.get_pose()
        return f"({pose.translation().X()}, {pose.translation().Y()}, {pose.rotation()}"

    def get_distance(self, left=True):
        if left:
            return self.left_distance
        else:
            return -self.right_distance

    def reset(self, new_pose: wpimath.geometry.Pose2d = wpimath.geometry.Pose2d()):
        self.odometry.resetPosition(
            new_pose, wpimath.geometry.Rotation2d.fromDegrees(self.getAngle())
        )
        self.left_encoder.setPosition(0)
        self.right_encoder.setPosition(0)

    @property
    def left_rate(self):
        return self.left_encoder.getVelocity()

    @property
    def right_rate(self):
        return -self.right_encoder.getVelocity()

    def execute(self):
        self.odometry.update(
            wpilib.geometry.Rotation2d(math.radians(self.getAngle())),
            self.left_encoder.getPosition(),
            -self.right_encoder.getPosition(),
        )
        self.left_distance = self.left_encoder.getPosition()
        self.right_distance = -self.right_encoder.getPosition()
