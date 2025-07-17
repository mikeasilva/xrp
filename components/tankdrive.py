import magicbot
from magicbot import feedback
import math
import wpilib.drive
import xrp


class CurvatureDrive:
    def __init__(
        self,
        cd_turn_nonlinearity=0.5,
        cd_neg_inertia_scalar=4.0,
        cd_sensitivity=0.9,
        drive_deadband=0.05,
        drive_slew=0.02,
    ):
        # Tuning constants
        self.CD_TURN_NONLINEARITY = cd_turn_nonlinearity
        self.CD_NEG_INERTIA_SCALAR = cd_neg_inertia_scalar
        self.CD_SENSITIVITY = cd_sensitivity
        self.DRIVE_DEADBAND = drive_deadband
        self.DRIVE_SLEW = drive_slew

        # Persistent state variables
        self.quick_stop_accumulator = 0.0
        self.neg_inertia_accumulator = 0.0
        self.prev_turn = 0.0
        self.prev_throttle = 0.0

    def _turn_remapping(self, iturn):
        """Apply a double sinusoidal remap to fine-tune small turn inputs."""
        denominator = math.sin(math.pi / 2 * self.CD_TURN_NONLINEARITY)
        first_remap = (
            math.sin(math.pi / 2 * self.CD_TURN_NONLINEARITY * iturn) / denominator
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

    def get_speed_and_rotation(self, ithrottle, iturn):
        """Compute left and right motor outputs based on throttle and turn input."""
        turn_in_place = False
        linear_cmd = ithrottle

        if abs(ithrottle) < self.DRIVE_DEADBAND and abs(iturn) > self.DRIVE_DEADBAND:
            linear_cmd = 0.0
            turn_in_place = True
        elif ithrottle - self.prev_throttle > self.DRIVE_SLEW:
            linear_cmd = self.prev_throttle + self.DRIVE_SLEW
        elif ithrottle - self.prev_throttle < -(self.DRIVE_SLEW * 2):
            linear_cmd = self.prev_throttle - (self.DRIVE_SLEW * 2)

        remapped_turn = self._turn_remapping(iturn)

        if turn_in_place:
            left = remapped_turn * abs(remapped_turn)
            right = -remapped_turn * abs(remapped_turn)
        else:
            neg_inertia_power = (iturn - self.prev_turn) * self.CD_NEG_INERTIA_SCALAR
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

        self.prev_turn = iturn
        self.prev_throttle = ithrottle

        return (left, right)


class TankDrive:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor
    # speed = magicbot.tunable(0.0)
    # rotation = magicbot.tunable(0.0)
    use_curvature_drive = magicbot.tunable(False)
    square_inputs = magicbot.tunable(True)
    # target_heading = magicbot.tunable(0.0)

    def setup(self):
        self.speed = 0.0
        self.rotation = 0.0
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.curvature_drive = CurvatureDrive()

    def execute(self):
        pass

    def go(self, speed: float, rotation: float):
        if self.use_curvature_drive:
            speed, rotation = self.curvature_drive.get_speed_and_rotation(
                speed, rotation
            )

        self.square_inputs = not self.use_curvature_drive
        self.speed = speed
        self.rotation = rotation
        self.drive.arcadeDrive(
            self.speed, self.rotation, squareInputs=self.square_inputs
        )

    def stop(self):
        self.speed = 0.0
        self.drive.stopMotor()

    def set_use_curvature_drive(self, use_curvature_drive: bool):
        """Enable or disable curvature drive mode."""
        self.use_curvature_drive = use_curvature_drive

    @feedback(key="Speed")
    def get_speed(self) -> float:
        """Get the speed passed into the drive."""
        return self.speed

    @feedback(key="Rotation")
    def get_rotation(self) -> float:
        """Get the rotation passed into the drive."""
        return self.rotation
