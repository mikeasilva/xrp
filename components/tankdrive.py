from wpilib.drive import DifferentialDrive
from magicbot import will_reset_to, feedback
import xrp
import wpilib


class TankDrive:
    _speed = will_reset_to(0.0)
    _rotation = will_reset_to(0.0)
    motors: dict[str, xrp.XRPMotor]
    encoders: dict[str, wpilib.Encoder]

    def setup(self):
        self.left_motor = self.motors["left_motor"]
        # We are going to invert the right motors
        self.right_motor = self.motors["right_motor"]
        self.right_motor.setInverted(True)
        # Check if there are follower motors, and if so, set them up
        if "right_follower" in self.motors:
            self.right_follower = self.motors["right_follower"]
            self.right_follower.setInverted(True)
            self.right_follower.follow(self.right_motor)
        if "left_follower" in self.motors:
            self.left_follower = self.motors["left_follower"]
            self.left_follower.follow(self.left_motor)

        # set up differential drive class
        self._drive = DifferentialDrive(self.left_motor, self.right_motor)

    def execute(self):
        self._drive.arcadeDrive(self._speed, self._rotation)

    def drive(self, speed: float, rotation: float) -> None:
        self._speed = speed
        self._rotation = rotation

    def stop(self) -> None:
        self._speed = 0.0
        self._rotation = 0.0
        self._drive.stopMotor()

    @feedback
    def speed(self) -> float:
        return self._speed

    @feedback
    def rotation(self) -> float:
        return self._rotation
