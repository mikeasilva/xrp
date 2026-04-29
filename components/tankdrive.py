import magicbot
import xrp
import wpilib
import wpilib.drive
import wpimath.kinematics
import wpimath.geometry
import components


class TankDrive:
    # Injected variables
    motors: dict[str, xrp.XRPMotor]
    encoders: dict[str, wpilib.Encoder]
    distance_per_pulse: float
    gyro: components.XRPGyro
    # Other variables
    _speed: float = 0.0
    _rotation: float = 0.0
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0
    left_distance: float = 0.0
    right_distance: float = 0.0

    def setup(self) -> None:
        # Set up motors
        self.left_motor = self.motors["left_motor"]
        self.left_motor.setSafetyEnabled(True)
        ## We are going to invert the right motors
        self.right_motor = self.motors["right_motor"]
        self.right_motor.setSafetyEnabled(True)
        self.right_motor.setInverted(True)
        ## Check if there are follower motors, and if so, set them up
        if "right_follower" in self.motors:
            self.right_follower = self.motors["right_follower"]
            self.right_follower.setSafetyEnabled(True)
            self.right_follower.setInverted(True)
            self.right_follower.follow(self.right_motor)
        if "left_follower" in self.motors:
            self.left_follower = self.motors["left_follower"]
            self.left_follower.setSafetyEnabled(True)
            self.left_follower.follow(self.left_motor)

        # Set up encoders
        self.right_encoder = self.encoders["right_encoder"]
        self.left_encoder = self.encoders["left_encoder"]
        self.reset_encoders()
        self.right_encoder.setDistancePerPulse(self.distance_per_pulse)
        self.left_encoder.setDistancePerPulse(self.distance_per_pulse)

        # Set up differential drive
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

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

    def execute(self) -> None:
        # Drive the robot using arcade drive with the current speed and rotation
        self._drive.arcadeDrive(self._speed, self._rotation)

        # Update the odometry and pose estimation
        self.left_distance = self.left_encoder.getDistance()
        self.right_distance = self.right_encoder.getDistance()
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
            self.right_encoder.getRate() - self.left_encoder.getRate()
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

    def drive(self, speed: float, rotation: float) -> None:
        self._speed = speed
        self._rotation = rotation

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def stop(self) -> None:
        self._speed = 0.0
        self._rotation = 0.0
        self._drive.stopMotor()

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
