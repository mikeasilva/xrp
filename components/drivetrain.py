from magicbot import feedback
import math
import wpilib
import wpilib.drive
import xrp


class DriveTrain:
    gyro: xrp.XRPGyro
    left_encoder: wpilib.Encoder
    left_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.reset_encoders()

    def execute(self):
        pass

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def go(self, throttle: float, rotation: float, square_inputs: bool = True) -> None:
        self.drive.arcadeDrive(throttle, rotation, squareInputs=square_inputs)
        # TODO: Check if the robot is moving and update it

    def move_forward(self, speed, heading):
        current_heading = self.gyro_angle()
        error = heading - current_heading

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
    def gyro_angle(self) -> float:
        angle_in_radians = self.gyro.getAngle()
        angle = math.degrees(angle_in_radians)
        return round(angle, 1)

    def is_moving(self) -> bool:
        return self.velocity() > 0

    def is_turning(self) -> bool:
        if abs(round(self.gyro.getRate(), 0)) == 0:
            return False
        return True

    @feedback(key="Right Encoder")
    def right_encoder_value(self) -> int:
        return self.right_encoder.getRaw()

    @feedback(key="Left Encoder")
    def left_encoder_value(self) -> int:
        return self.left_encoder.getRaw()

    @feedback(key="Velocity (inch per sec)")
    def velocity(self) -> float:
        speed = (self.right_encoder.getRate() + self.left_encoder.getRate()) / 2
        return round(abs(speed), 1)
    
    @feedback(key="Distance")
    def distance(self) -> float:
        distance = (self.right_encoder.getDistance() + self.left_encoder.getDistance()) / 2
        return round(distance, 1)
