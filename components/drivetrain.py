from magicbot import feedback
import math
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

    ENCODER_VALUES = {"right": 0, "left": 0}

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

    @feedback(key="Gyro Angle (degrees)")
    def gyro_angle(self):
        angle_in_radians = self.gyro.getAngle()
        angle = math.degrees(angle_in_radians)
        return round(angle, 1)

    @feedback(key="Is Moving")
    def is_moving(self) -> bool:
        if (self.ENCODER_VALUES["left"] != self.left_encoder_value()) or (
            self.ENCODER_VALUES["right"] != self.right_encoder_value()
        ):
            self.ENCODER_VALUES["left"] = self.left_encoder_value()
            self.ENCODER_VALUES["right"] = self.right_encoder_value()
            return True
        return False

    @feedback(key="Is Turning")
    def is_turning(self) -> bool:
        if abs(round(self.gyro.getRate(), 0)) == 0:
            return False
        return True

    @feedback(key="Right Encoder")
    def right_encoder_value(self):
        return self.right_encoder.getRaw()

    @feedback(key="Left Encoder")
    def left_encoder_value(self):
        return self.left_encoder.getRaw()
