import wpilib
import wpilib.drive
import wpimath.controller
import xrp


class XRPTankDrive:
    distance_pid_values: dict
    heading_pid_values: dict
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor
    left_encoder: wpilib.Encoder
    right_encoder: wpilib.Encoder
    control_style: str

    def setup(self) -> None:
        # Initialize variables
        self._speed = 0.0
        self._rotation = 0.0
        self._left_speed = 0.0
        self._right_speed = 0.0
        self._initial_heading = 0.0
        self._initial_distance = 0.0
        self.distance_setpoint = None
        self.heading_setpoint = None

        # Set up differential drive
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

        # Set up PID controllers
        self.distance_pid = wpimath.controller.PIDController(**self.distance_pid_values)
        self.heading_pid = wpimath.controller.PIDController(**self.heading_pid_values)

        self.reset_encoders()

    def execute(self) -> None:
        if self.control_style == "arcade":
            # Drive the robot using arcade drive with the current speed and rotation
            self._drive.arcadeDrive(self._speed, self._rotation)
        elif self.control_style in ["cheesey", "curvature"]:
            self._drive.curvatureDrive(self._speed, self._rotation, True)
        elif self.control_style == "tank":
            self._drive.tankDrive(self._left_speed, self._right_speed)
        else:
            pass

    def drive(
        self,
        speed: float = 0.0,
        rotation: float = 0.0,
        left_speed: float = 0.0,
        right_speed: float = 0.0,
    ) -> None:
        self._speed = speed
        self._rotation = rotation
        self._left_speed = left_speed
        self._right_speed = right_speed

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def stop(self) -> None:
        self._speed = 0.0
        self._rotation = 0.0
        self._drive.stopMotor()
