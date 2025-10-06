from magicbot import feedback
import math
import wpilib
import wpilib.drive
import wpimath.geometry
import wpimath.kinematics
import xrp


class DriveTrain:
    gyro: xrp.XRPGyro
    left_encoder: wpilib.Encoder
    left_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.reset_encoders()
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d(self.gyro.getAngle()),
            self.left_encoder.getDistance(),
            self.right_encoder.getDistance(),
        )

    def execute(self):
        pass

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def go(self, throttle: float, rotation: float, square_inputs: bool = True) -> None:
        self.drive.arcadeDrive(throttle, rotation, squareInputs=square_inputs)
        # TODO: Check if the robot is moving and update it

    def move_forward(self, speed, heading):
        current_heading = self.heading_in_degrees()
        error = heading - current_heading

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def reset_gyro(self) -> None:
        self.gyro.reset()

    def stop(self) -> None:
        self.drive.stopMotor()
        # TODO: Update the robot is moving parameter

    def update_odometry(self) -> None:
        self.odometry.update(
            wpimath.geometry.Rotation2d(self.gyro.getAngle()),
            self.left_encoder.getDistance(),
            self.right_encoder.getDistance(),
        )

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @feedback(key="Distance")
    def distance(self) -> float:
        distance = (
            self.right_encoder.getDistance() + self.left_encoder.getDistance()
        ) / 2
        return round(distance, 1)

    @feedback(key="Gyro Angle (degrees)")
    def heading_in_degrees(self) -> float:
        angle_in_radians = self.gyro.getAngle()
        angle = math.degrees(angle_in_radians)
        return round(angle, 1)

    @feedback(key="Pose X")
    def pose_x(self):
        return round(self.odometry.getPose().X(), 1)

    @feedback(key="Pose Y")
    def pose_y(self):
        return round(self.odometry.getPose().Y(), 1)

    def is_moving(self) -> bool:
        return self.velocity() > 0

    def is_turning(self) -> bool:
        return abs(round(self.gyro.getRate(), 0)) != 0

    @feedback(key="Velocity (inch per sec)")
    def velocity(self) -> float:
        speed = (self.right_encoder.getRate() + self.left_encoder.getRate()) / 2
        return round(abs(speed), 1)
