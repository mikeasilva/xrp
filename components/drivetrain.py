import magicbot
import math
import wpilib
import wpilib.drive
import wpimath.controller
import wpimath.geometry
import wpimath.kinematics
import xrp


class DriveTrain:
    distance_pid_values: dict
    heading_pid_values: dict
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor
    left_encoder: wpilib.Encoder
    right_encoder: wpilib.Encoder
    gyro: xrp.XRPGyro
    control_style: str
    gyro_noise_threshold: float
    

    def setup(self) -> None:
        # Initialize variables
        self.distance_setpoint = -999.0
        self.heading_setpoint = -999.0
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        self.left_distance = 0.0
        self.right_distance = 0.0
        self._speed = 0.0
        self._rotation = 0.0
        self._left_speed = 0.0
        self._right_speed = 0.0
        self._initial_heading = 0.0
        self._initial_distance = 0.0
        self._previous_rotational_rates = {"pitch": 0.0, "roll": 0.0, "yaw": 0.0}
        self._timer = wpilib.Timer()
        self._timer.start()

        # Set up differential drive
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

        # Set up PID controllers
        self.distance_pid = wpimath.controller.PIDController(**self.distance_pid_values)
        self.heading_pid = wpimath.controller.PIDController(**self.heading_pid_values)

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

        self.reset_encoders()
        self.reset_gyro()

    def execute(self) -> None:
        # Double integrate the gyro values to get rotation
        ## Get the current rotational rates, apply noise filtering, and integrate to get the rotation
        current_rotational_rates = {
            "pitch": self._noise_filter(self.gyro.getRateX(), self.gyro_noise_threshold),
            "roll": self._noise_filter(self.gyro.getRateY(), self.gyro_noise_threshold),
            "yaw": self._noise_filter(self.gyro.getRateZ(), self.gyro_noise_threshold),
        }
        ## Calculate the average rotational rate for integration
        average_rotational_rate = {}
        for k in current_rotational_rates:
            average_rotational_rate[k] = (current_rotational_rates[k] + self._previous_rotational_rates[k]) / 2.0
        ## Integrate the average rotational rate around the Z-axis to get the rotation in radians
        elapsed_time = self._timer.get()
        self.pitch += average_rotational_rate["pitch"] * elapsed_time
        self.roll += average_rotational_rate["roll"] * elapsed_time
        self.yaw += average_rotational_rate["yaw"] * elapsed_time
        ## Update the previous rotational rates and reset the timer for the next update
        self._previous_rotational_rates = current_rotational_rates
        self._timer.reset()

        # Update the odometry and pose estimation
        ## Update the left and right distances from the encoders
        self.left_distance = self.left_encoder.getDistance()
        self.right_distance = self.right_encoder.getDistance()
        ## Update the odometry with the current gyro rate and encoder distances
        self.odometry.update(
            wpimath.geometry.Rotation2d(self.yaw),
            self.left_distance,
            self.right_distance,
        )
        self.pose = self.odometry.getPose()

        # Update the chassis speed based on the current encoder rates and gyro rate
        ## Average the left and right encoder rates for the linear velocity
        linear_velocity = (self.right_encoder.getRate() - self.left_encoder.getRate()) / 2
        ## Apply a filter to the linear velocity
        self.linear_velocity = self._noise_filter(linear_velocity, 0.001)
        ## The angular velocity is the rate of change of the gyro angle
        ## Apply a filter to the angular velocity
        self.angular_velocity = self._noise_filter(self.gyro.getRate(), 0.001)
        ## Update the chassis speed
        self.chassis_speed = wpimath.kinematics.ChassisSpeeds(self.linear_velocity, 0, self.angular_velocity)

        # Use the PID controllers to calculate adjustments
        heading_adjustment = self.heading_pid.calculate(self.yaw, self.heading_setpoint) if self.heading_setpoint != -999.0 else 0.0
        distance_adjustment = self.distance_pid.calculate(self.odometry.getPose().X(), self.distance_setpoint) if self.distance_setpoint != -999.0 else 0.0
        if heading_adjustment != 0.0 or distance_adjustment != 0.0:
            adjustment = (heading_adjustment + distance_adjustment) / 2
        elif heading_adjustment != 0.0:
            adjustment = heading_adjustment
        elif distance_adjustment != 0.0:
            adjustment = distance_adjustment
        else:
            adjustment = 0.0

        if adjustment != 0.0:
            self._drive.tankDrive(adjustment, -adjustment)
        # Drive the robot based on the current control style and speed/rotation values
        elif self.control_style == "arcade":
            # Drive the robot using arcade drive with the current speed and rotation
            self._drive.arcadeDrive(self._speed, self._rotation)
        elif self.control_style in ["cheesey", "curvature"]:
            self._drive.curvatureDrive(self._speed, self._rotation, True)
        elif self.control_style == "tank":
            self._drive.tankDrive(self._left_speed, self._right_speed)
        else:
            pass

    def drive(self, speed: float = 0.0, rotation: float = 0.0, left_speed: float = 0.0, right_speed: float = 0.0) -> None:
        self._speed = speed
        self._rotation = rotation
        if rotation == 0:
            if self.heading_setpoint == -999.0:
                self.set_heading_setpoint(self.yaw)
        else:
            self.set_heading_setpoint(-999.0)

        self._left_speed = left_speed
        self._right_speed = right_speed

    def _noise_filter(self, val, threshold):
        if abs(val) < threshold:
            return 0.0
        return val

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def reset_gyro(self) -> None:
        self.gyro.reset()
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.angle = 0.0
        self._previous_rotational_rates = {"pitch": 0.0, "roll": 0.0, "yaw": 0.0}

    def set_heading_setpoint(self, val) -> None:
        self.heading_setpoint = val

    def stop(self) -> None:
        self._speed = 0.0
        self._rotation = 0.0
        self._drive.stopMotor()

    @magicbot.feedback(key="heading setpoint")
    def get_heading_setpoint(self) -> float:
        return self.heading_setpoint

    @magicbot.feedback(key="pitch")
    def get_pitch(self) -> float:
        # The rotation in radians
        return self.pitch

    @magicbot.feedback(key="roll")
    def get_roll(self) -> float:
        # The rotation in radians
        return self.roll

    @magicbot.feedback(key="yaw")
    def get_yaw(self) -> float:
        # The rotation in radians
        return self.yaw

    @magicbot.feedback
    def heading(self) -> float:
        # The heading in degrees, normalized to [0, 360)
        return math.degrees(self.yaw) % 360
