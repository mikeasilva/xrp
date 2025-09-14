from magicbot import feedback
import wpilib
import wpilib.drive
import wpimath.units
import xrp


class DriveTrain:
    gyro: xrp.XRPGyro
    left_encoder: wpilib.Encoder
    left_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def execute(self):
        pass

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def go(self, throttle: float, rotation: float, square_inputs: bool = True) -> None:
        self.drive.arcadeDrive(throttle, rotation, squareInputs=square_inputs)
        # TODO: Check if the robot is moving and update it

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def reset_gyro(self) -> None:
        self.gyro.reset()

    def stop(self) -> None:
        self.drive.stopMotor()
        # TODO: Update the robot is moving parameter

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @feedback(key="Gyro Angle")
    def gyro_angle(self) -> wpimath.units.radians:
        return self.gyro.getAngle()

    @feedback(key="Is Moving")
    def is_moving(self) -> bool:
        return (not self.left_encoder.getStopped()) or (
            not self.right_encoder.getStopped()
        )
