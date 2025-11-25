import magicbot
import wpilib
import wpilib.drive
import xrp


class DriveTrain:
    left_motor: xrp.XRPMotor
    left_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder

    def execute(self):
        pass

    def setup(self):
        self.right_motor.setInverted(True)
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def reset_encoders(self):
        self.left_encoder.reset()
        self.right_encoder.reset()

    def stop(self):
        self.drive.stopMotor()

    def straight(self, distance: float, unit: str = "cm", effort: float = 0.5):
        pass

    def turn(self, degree, effort: float = 0.5):
        pass

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Left Encoder")
    def get_left_encoder(self) -> float:
        return self.left_encoder.getDistance()

    @magicbot.feedback(key="Right Encoder")
    def get_right_encoder(self) -> float:
        return self.right_encoder.getDistance()
