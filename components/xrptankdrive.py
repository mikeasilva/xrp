import magicbot
import math
import xrp
import wpilib
import wpilib.drive
import constants


class XRPTankDrive:
    # Other variables
    _speed: float = 0.0
    _rotation: float = 0.0

    def setup(self) -> None:
        # Set up motors
        # Distance per pulse is pi * wheel diameter / pulses per revolution * gear ratio
        distance_per_pulse = (
            math.pi
            * constants.Robot.WHEEL_DIAMETER_M
            / (constants.Robot.PULSES_PER_REVOLUTION * constants.Robot.GEAR_RATIO)
        )

        self.left_motor = xrp.XRPMotor(constants.Ids.LEFT_MOTOR)
        self.left_motor.setSafetyEnabled(True)
        ## We are going to invert the right motors
        self.right_motor = xrp.XRPMotor(constants.Ids.RIGHT_MOTOR)
        self.right_motor.setSafetyEnabled(True)
        self.right_motor.setInverted(True)

        # Set up encoders
        self.right_encoder = wpilib.Encoder(*constants.Ids.RIGHT_ENCODER)
        self.left_encoder = wpilib.Encoder(*constants.Ids.LEFT_ENCODER)
        self.reset_encoders()
        self.right_encoder.setDistancePerPulse(distance_per_pulse)
        self.right_encoder.setReverseDirection(True)
        self.left_encoder.setDistancePerPulse(distance_per_pulse)

        # Set up differential drive
        self._drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def execute(self) -> None:
        # Drive the robot using arcade drive with the current speed and rotation
        self._drive.arcadeDrive(self._speed, self._rotation)

    def drive(self, speed: float, rotation: float) -> None:
        self._speed = speed
        self._rotation = rotation

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def stop(self) -> None:
        self._speed = 0.0
        self._rotation = 0.0
        self._drive.stopMotor()
