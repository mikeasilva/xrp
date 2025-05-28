import wpilib
import constants
import math


class XRPEncoder:
    encoder: wpilib.Encoder

    def __init__(self, dio_a_channel: int, dio_b_channel: int) -> None:
        self.encoder = wpilib.Encoder(dio_a_channel, dio_b_channel)
        self.encoder.setDistancePerPulse(
            (math.pi * constants.WHEEL_DIAMETER_INCH)
            / (constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO)
        )

    def execute(self) -> None:
        pass

    def get_distance(self) -> float:
        return self.encoder.getDistance()

    def reset(self) -> None:
        self.encoder.reset()
