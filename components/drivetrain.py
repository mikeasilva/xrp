import wpilib
import wpilib.drive
import xrp


class Drivetrain:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def move(self, speed, rotation):
        self.drive.arcadeDrive(speed, rotation, squareInputs=False)

    def stop(self):
        self.drive.stopMotor()

    def execute(self):
        pass
