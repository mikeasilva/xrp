from magicbot import feedback
import wpilib.drive
import xrp
import math


class CurvatureDrive:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.mode = "curvature"  # Default to curvature drive
        self.left = 0.0
        self.right = 0.0

        # Tuning constants
        self.CD_TURN_NONLINEARITY = 0.5
        self.CD_NEG_INERTIA_SCALAR = 4.0
        self.CD_SENSITIVITY = 0.9
        self.DRIVE_DEADBAND = 0.05
        self.DRIVE_SLEW = 0.2

        # Persistent state variables
        self.quick_stop_accumulator = 0.0
        self.neg_inertia_accumulator = 0.0
        self.prev_turn = 0.0
        self.prev_throttle = 0.0

    def execute(self):
        pass

    def _turn_remapping(self, turn):
        """Apply a double sinusoidal remap to fine-tune small turn inputs."""
        denominator = math.sin(math.pi / 2 * self.CD_TURN_NONLINEARITY)
        first_remap = (
            math.sin(math.pi / 2 * self.CD_TURN_NONLINEARITY * turn) / denominator
        )
        return (
            math.sin(math.pi / 2 * self.CD_TURN_NONLINEARITY * first_remap)
            / denominator
        )

    def _update_accumulators(self):
        """Clamp the accumulators between -1 and 1."""
        if self.neg_inertia_accumulator > 1:
            self.neg_inertia_accumulator -= 1
        elif self.neg_inertia_accumulator < -1:
            self.neg_inertia_accumulator += 1
        else:
            self.neg_inertia_accumulator = 0

        if self.quick_stop_accumulator > 1:
            self.quick_stop_accumulator -= 1
        elif self.quick_stop_accumulator < -1:
            self.quick_stop_accumulator += 1
        else:
            self.quick_stop_accumulator = 0.0

    def get_left_and_right(self, throttle, turn):
        """Compute left and right motor outputs based on throttle and turn input."""
        turn_in_place = False
        linear_cmd = throttle

        if abs(throttle) < self.DRIVE_DEADBAND and abs(turn) > self.DRIVE_DEADBAND:
            linear_cmd = 0.0
            turn_in_place = True
        elif throttle - self.prev_throttle > self.DRIVE_SLEW:
            linear_cmd = self.prev_throttle + self.DRIVE_SLEW
        elif throttle - self.prev_throttle < -(self.DRIVE_SLEW * 2):
            linear_cmd = self.prev_throttle - (self.DRIVE_SLEW * 2)

        remapped_turn = self._turn_remapping(turn)

        if turn_in_place:
            left = remapped_turn * abs(remapped_turn)
            right = -remapped_turn * abs(remapped_turn)
        else:
            neg_inertia_power = (turn - self.prev_turn) * self.CD_NEG_INERTIA_SCALAR
            self.neg_inertia_accumulator += neg_inertia_power

            angular_cmd = (
                abs(linear_cmd)
                * (remapped_turn + self.neg_inertia_accumulator)
                * self.CD_SENSITIVITY
                - self.quick_stop_accumulator
            )

            left = linear_cmd + angular_cmd
            right = linear_cmd - angular_cmd

            self._update_accumulators()

        self.prev_turn = turn
        self.prev_throttle = throttle

        return (left, right)

    def go(self, throttle: float, turn: float):
        """
        Drive the robot using curvature drive.

        :param throttle: The forward/backward speed (-1 to 1).
        :param turn: The turning speed (-1 to 1).
        """
        self.left, self.right = self.get_left_and_right(throttle, turn)
        self.drive.tankDrive(self.left, self.right)

    def stop(self):
        self.speed = 0.0
        self.drive.stopMotor()

    def set_mode(self, mode) -> None:
        self.mode = mode

    @feedback(key="Mode")
    def get_mode(self) -> str:
        """Get the current drive mode."""
        return self.mode

    @feedback(key="Left")
    def get_left(self) -> float:
        """Get the speed passed into the drive."""
        return self.left

    @feedback(key="Right")
    def get_right(self) -> float:
        """Get the rotation passed into the drive."""
        return self.right
