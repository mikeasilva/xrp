import xrp
from wpilib.drive import DifferentialDrive
import wpilib


class DriveTrain:
    gyro: xrp.XRPGyro
    left_encoder: wpilib.Encoder
    left_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor

    def setup(self):
        self.drive = DifferentialDrive(self.left_motor, self.right_motor)

    def execute(self):
        pass

    def go(self, throttle: float, rotation: float, square_inputs: bool = True):
        self.drive.arcadeDrive(throttle, rotation, squareInputs=square_inputs)
        # TODO: Check if the robot is moving and update it

    def stop(self):
        self.drive.stopMotor()
        # TODO: Update the robot is moving parameter
