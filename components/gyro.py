import magicbot
import math
import wpilib
import xrp


class XRPGyro:
    noise_threshold: float
    _rotation: float = 0.0
    _previous_rotational_rates: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def setup(self) -> None:
        self._gyro = xrp.XRPGyro()
        self._timer = wpilib.Timer()
        self._timer.start()

    def execute(self) -> None:
        # Get the current rotational rates, apply noise filtering, and integrate to get the rotation
        current_rotational_rates = (
            self._noise_filter(self._gyro.getRateX()),
            self._noise_filter(self._gyro.getRateY()),
            self._noise_filter(self._gyro.getRateZ()),
        )
        # Get the elapsed time since the last update and calculate the average rotational rate for integration
        elapsed_time = self._timer.get()
        average_rotational_rate = (
            (current_rotational_rates[0] + self._previous_rotational_rates[0]) / 2.0,
            (current_rotational_rates[1] + self._previous_rotational_rates[1]) / 2.0,
            (current_rotational_rates[2] + self._previous_rotational_rates[2]) / 2.0,
        )
        # Integrate the average rotational rate around the Z-axis to get the rotation in radians
        self._rotation += average_rotational_rate[2] * elapsed_time
        # Update the previous rotational rates and reset the timer for the next update
        self._previous_rotational_rates = current_rotational_rates
        self._timer.reset()

    def reset(self) -> None:
        self._gyro.reset()
        self._rotation = 0.0
        self._previous_rotational_rates = (0.0, 0.0, 0.0)

    '''
    @magicbot.feedback
    def rotation(self) -> float:
        # The rotation in radians
        return self._rotation
    '''

    @magicbot.feedback
    def heading(self) -> float:
        # The heading in degrees, normalized to [0, 360)
        return math.degrees(self._rotation) % 360

    def _noise_filter(self, val):
        if abs(val) < self.noise_threshold:
            return 0.0
        return val
