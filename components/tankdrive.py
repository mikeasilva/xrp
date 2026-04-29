import magicbot
import xrp
import wpilib
import wpilib.drive
import wpimath.kinematics
import wpimath.geometry
import components


class TankDrive:
    _speed: float = 0.0
    _rotation: float = 0.0
    left_distance: float = 0.0
    right_distance: float = 0.0
    motors: dict[str, xrp.XRPMotor]
    encoders: dict[str, wpilib.Encoder]
    distance_per_pulse: float
    gyro: components.XRPGyro

    def setup(self) -> None:
        self.pose = wpimath.geometry.Pose2d(0, 0, wpimath.geometry.Rotation2d(0))
        self.left_motor = self.motors["left_motor"]
        self.left_motor.setSafetyEnabled(True)
        # We are going to invert the right motors
        self.right_motor = self.motors["right_motor"]
        self.right_motor.setSafetyEnabled(True)
        self.right_motor.setInverted(True)
        # Check if there are follower motors, and if so, set them up
        if "right_follower" in self.motors:
            self.right_follower = self.motors["right_follower"]
            self.right_follower.setSafetyEnabled(True)
            self.right_follower.setInverted(True)
            self.right_follower.follow(self.right_motor)
        if "left_follower" in self.motors:
            self.left_follower = self.motors["left_follower"]
            self.left_follower.setSafetyEnabled(True)
            self.left_follower.follow(self.left_motor)

        self.right_encoder = self.encoders["right_encoder"]
        self.right_encoder.setDistancePerPulse(self.distance_per_pulse)
        self.left_encoder = self.encoders["left_encoder"]
        self.left_encoder.setDistancePerPulse(self.distance_per_pulse)
        self.reset_encoders()

        # set up differential drive class
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

        self._odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d(self.gyro.angle),
            self.left_distance,
            self.right_distance,
            wpimath.geometry.Pose2d(0, 0, wpimath.geometry.Rotation2d(0)),
        )

    def execute(self) -> None:
        self._drive.arcadeDrive(self._speed, self._rotation)
        self.left_distance = self.left_encoder.getDistance()
        self.right_distance = self.right_encoder.getDistance()

        self._odometry.update(
            wpimath.geometry.Rotation2d(self.gyro.angle),
            self.left_distance,
            self.right_distance,
        )
        self.pose = self._odometry.getPose()

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
    def speed(self) -> float:
        return self._speed

    @magicbot.feedback
    def rotation(self) -> float:
        return self._rotation

    @magicbot.feedback
    def distance(self) -> float:
        return (self.right_distance + self.left_distance) / 2

    @magicbot.feedback(key="pose x")
    def get_pose_x(self) -> float:
        return self.pose.X()

    @magicbot.feedback(key="pose y")
    def get_pose_y(self) -> float:
        return self.pose.Y()
