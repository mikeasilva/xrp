import magicbot
import xrp
import wpilib
import wpilib.drive


class TankDrive:
    _speed: float = 0.0
    _rotation = 0.0
    _left_distance: float = 0.0
    _right_distance: float = 0.0
    motors: dict[str, xrp.XRPMotor]
    encoders: dict[str, wpilib.Encoder]

    def setup(self) -> None:
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
        self.left_encoder = self.encoders["left_encoder"]

        # set up differential drive class
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def execute(self) -> None:
        self._drive.arcadeDrive(self._speed, self._rotation)

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
