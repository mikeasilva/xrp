import magicbot
import wpilib.drive
import xrp


class Drivetrain:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor
    speed = magicbot.tunable(0.0)

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def move(self, speed: float, rotation: float):
        self.speed = speed
        self.drive.arcadeDrive(speed, rotation, squareInputs=False)

    def stop(self):
        self.speed = 0.0
        self.drive.stopMotor()

    def execute(self):
        pass
