import magicbot

# import ntcore
import wpilib.drive
import xrp


class TankDrive:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor
    speed = magicbot.tunable(0.0)
    target_heading = magicbot.tunable(0.0)

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def go(self, speed: float, rotation: float):
        self.speed = speed
        self.drive.arcadeDrive(speed, rotation, squareInputs=True)

    def stop(self):
        self.speed = 0.0
        self.drive.stopMotor()
