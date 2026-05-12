import magicbot
import wpilib
import wpimath.kinematics
import wpimath.geometry
import xrp


class Odometery:
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0
    left_distance: float = 0.0
    right_distance: float = 0.0
    gyro: xrp.XRPGyro
    left_encoder: wpilib.Encoder
    right_encoder: wpilib.Encoder
    noise_threshold: float
    angle: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0
    _previous_rotational_rates: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def setup(self):
        self._timer = wpilib.Timer()
        self._timer.start()
        # Set up odometry
        self.pose = wpimath.geometry.Pose2d(0, 0, wpimath.geometry.Rotation2d(0))
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d(0),
            self.left_distance,
            self.right_distance,
            self.pose,
        )

        # Set up chassis speed
        self.chassis_speed = wpimath.kinematics.ChassisSpeeds(
            self.linear_velocity, 0, self.angular_velocity
        )

    def execute(self):
        # Get the current rotational rates, apply noise filtering, and integrate to get the rotation
        current_rotational_rates = (
            self._noise_filter(self.gyro.getRateX()),
            self._noise_filter(self.gyro.getRateY()),
            self._noise_filter(self.gyro.getRateZ()),
        )

        # Get the elapsed time since the last update and calculate the average rotational rate for integration
        elapsed_time = self._timer.get()
        average_rotational_rate = (
            (current_rotational_rates[0] + self._previous_rotational_rates[0]) / 2.0,
            (current_rotational_rates[1] + self._previous_rotational_rates[1]) / 2.0,
            (current_rotational_rates[2] + self._previous_rotational_rates[2]) / 2.0,
        )

        # Integrate the average rotational rate around the Z-axis to get the rotation in radians
        self.pitch += average_rotational_rate[0] * elapsed_time
        self.roll += average_rotational_rate[1] * elapsed_time
        self.yaw += average_rotational_rate[2] * elapsed_time
        self.angle += average_rotational_rate[2] * elapsed_time

        # Update the previous rotational rates and reset the timer for the next update
        self._previous_rotational_rates = current_rotational_rates
        self._timer.reset()

        # Update the odometry and pose estimation
        self.left_distance = self.tankdrive.left_encoder.getDistance()
        self.right_distance = self.tankdrive.right_encoder.getDistance()
        ## Update the odometry with the current gyro rate and encoder distances
        self.odometry.update(
            wpimath.geometry.Rotation2d(self.angle),
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

    def _noise_filter(self, val):
        if abs(val) < self.noise_threshold:
            return 0.0
        return val

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
