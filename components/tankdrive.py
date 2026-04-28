import magicbot
import xrp
import wpilib
import wpilib.drive


class TankDrive:
    _speed = 0.0
    _rotation = 0.0
    _driving: bool = False
    motors: dict[str, xrp.XRPMotor]
    encoders: dict[str, wpilib.Encoder]

    def setup(self):
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

        # set up differential drive class
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def execute(self):
        self._drive.arcadeDrive(self._speed, self._rotation)

    def drive(self, speed: float, rotation: float) -> None:
        self._speed = speed
        self._rotation = rotation

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
