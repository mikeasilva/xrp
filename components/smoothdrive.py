"""Smooth joystick input and drive either a tank or swerve drivetrain.

What it does, in order:

1. **Deadband** removes stick drift near the center.
2. **Response curve** gives finer control at low stick values.
3. **Mode scaling** multiplies by the maximum for the current mode
   ("normal", "boost", or "precision").
4. **Slew limiting** ramps the output toward the target instead of jumping,
   and lets the robot slow down faster than it speeds up.
5. **Heading hold** keeps the robot pointed straight when the driver is
   translating but not rotating.

Heading hold rules:

* Rotation stick used: the heading target is cleared and the driver steers.
* Rotation stick centered and translating: after the robot has stopped
  turning for ``settle_time`` seconds, the current heading becomes the target
  and a PID holds it.
* Not translating: the target is cleared, so the robot never fights to return
  to an old heading after being bumped while stopped.
* Gyro disconnected: heading hold is turned off.

Usage in a RobotPy MagicBot project. Configure ``drivetrain_type`` as
``"tank"`` or ``"swerve"`` and declare one ``SmoothDrive`` component::

    from components.gyro import Gyro
    from components.smoothdrive import SmoothDrive

    class Robot(MagicRobot):
        gyro: Gyro
        drivetrain: SmoothDrive

        def createObjects(self):
            self.drivetrain_type = "swerve"
            self.drivetrain_components = {
                # Configure motor, encoder, offset, and PID keys for all modules.
            }
            self.drivetrain_module_locations = (...)  # four Translation2d values
            self.drivetrain_max_speed_mps = 4.0
            self.drivetrain_max_angular_speed_rps = 6.0

        def teleopPeriodic(self):
            self.drivetrain.drive(
                fwd=-self.stick.getLeftY(),
                strafe=-self.stick.getLeftX(),
                rot=-self.stick.getRightX(),
            )

For tank, configure ``drivetrain_components`` with ``left_motor`` and
``right_motor``, set ``drivetrain_track_width`` and
``drivetrain_max_speed_mps``. Encoders are optional and enable odometry when
both are provided. Tank drive ignores strafe.

For swerve, configure ``drivetrain_module_locations`` (front-left,
front-right, back-left, back-right), ``drivetrain_max_speed_mps``, and
``drivetrain_max_angular_speed_rps``. Supply each module's hardware in
``drivetrain_components`` using keys of the form
``<module>_drive_motor``, ``<module>_steering_motor``,
``<module>_drive_encoder``, ``<module>_steering_encoder``,
``<module>_steering_offset_degrees``, ``<module>_drive_pid``, and
``<module>_steering_pid``. Replace ``<module>`` with ``front_left``,
``front_right``, ``back_left``, or ``back_right``.

All tunables (maximums, slew rates, heading-hold gains) appear under this
component in NetworkTables. Speeds are in m/s and rad/s.

``control_loop_wait_time`` is the loop period. MagicBot's default is 0.02 s.
If your Robot class sets a different ``control_loop_wait_time``, MagicBot
passes it in automatically.
"""

from __future__ import annotations

import math
from typing import Any, overload

import wpilib
import wpilib.drive
from magicbot import feedback, tunable, will_reset_to
from wpimath import applyDeadband
from wpimath import units as wpimath_units
from wpimath.controller import PIDController
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from wpimath.kinematics import (
    ChassisSpeeds,
    DifferentialDriveKinematics,
    DifferentialDriveOdometry,
    SwerveDrive4Kinematics,
    SwerveDrive4Odometry,
    SwerveModulePosition,
)

from .gyro import Gyro
from .swervemodule import SwerveModule


class SmoothDrive:
    """Smooth driver input and control a tank or swerve drivetrain."""

    # MagicBot injects values from robot attributes named after this component.
    type: str
    gyro: Gyro
    components: dict[str, Any]
    track_width: float = 0.6
    units: str = "meters"
    max_speed_mps: float = 3.0
    max_angular_speed_rps: float = 6.0
    module_locations: tuple[Translation2d, ...] = ()
    control_loop_wait_time: float = 0.02

    # Input shaping
    deadband = tunable(0.08)
    translation_curve = tunable(2.0)  # 1.0 = linear, 2.0 = squared
    rotation_curve = tunable(2.0)

    # Maximums per mode (real units)
    max_speed_normal = tunable(3.0)  # m/s
    max_speed_boost = tunable(4.5)
    max_speed_precision = tunable(1.0)
    max_rot_normal = tunable(3.0)  # rad/s
    max_rot_boost = tunable(4.0)
    max_rot_precision = tunable(1.5)

    # Slew rates (base values, normal mode)
    translation_accel = tunable(6.0)  # m/s^2
    translation_decel = tunable(12.0)  # m/s^2, faster so the driver can stop
    rotation_accel = tunable(12.0)  # rad/s^2
    rotation_decel = tunable(20.0)  # rad/s^2

    # Slew rate multipliers for the other modes
    boost_slew_scale = tunable(0.75)  # gentler, protects traction at speed
    precision_slew_scale = tunable(0.5)  # gentler, for fine positioning

    # Heading hold
    heading_hold_enabled = tunable(True)
    hold_kp = tunable(4.0)  # rad/s of correction per rad of error
    hold_ki = tunable(0.0)
    hold_kd = tunable(0.0)
    settle_rate_dps = tunable(8.0)  # must turn slower than this to capture
    settle_time = tunable(0.1)  # seconds below settle_rate_dps to capture
    hold_max_fraction = tunable(0.6)  # hold correction limit, fraction of max rot

    # Inputs, cleared to 0 every loop so stale values can't stick
    fwd_input = will_reset_to(0.0)
    strafe_input = will_reset_to(0.0)
    rot_input = will_reset_to(0.0)

    @staticmethod
    def apply_curve(value: float, exponent: float) -> float:
        """Reshape a stick value while keeping its sign and the -1..1 range."""
        return math.copysign(abs(value) ** exponent, value)

    @staticmethod
    def slew_scalar(
        current: float, target: float, accel: float, decel: float, dt: float
    ) -> float:
        """Move ``current`` toward ``target`` without exceeding the allowed rate.

        ``accel`` applies when speed is growing away from zero. ``decel``
        applies when speed is shrinking or reversing. Both are positive, in
        units per second squared.
        """
        speeding_up = abs(target) > abs(current) and (
            current == 0.0 or math.copysign(1.0, target) == math.copysign(1.0, current)
        )
        max_step = (accel if speeding_up else decel) * dt
        return current + max(-max_step, min(max_step, target - current))

    @staticmethod
    def slew_vector(
        current: tuple[float, float],
        target: tuple[float, float],
        accel: float,
        decel: float,
        dt: float,
    ) -> tuple[float, float]:
        """Move a 2D vector toward a target, limiting the size of the change.

        Limiting the whole vector (instead of x and y separately) makes
        diagonal acceleration feel the same as straight-line acceleration.
        """
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        distance = math.hypot(dx, dy)
        if distance < 1e-9:
            return target

        speeding_up = math.hypot(*target) > math.hypot(*current)
        max_step = (accel if speeding_up else decel) * dt
        if distance <= max_step:
            return target
        scale = max_step / distance
        return (current[0] + dx * scale, current[1] + dy * scale)

    def setup(self) -> None:
        """Validate and initialize the selected drivetrain and controls."""
        self._type = self.type.strip().lower()
        if self._type not in ("tank", "swerve"):
            raise ValueError(
                f"Unknown smoothdrive_type {self.type!r}; use 'tank' or 'swerve'"
            )

        self._is_simulation = wpilib.RobotBase.isSimulation()
        self.pose = Pose2d()
        self._tank_simulation_readings: tuple[float, float, Rotation2d] | None = None
        self._swerve_simulation_heading: Rotation2d | None = None
        self._stop_requested = False

        if self._type == "tank":
            self._setup_tank()
        else:
            self._setup_swerve()

        self._mode = "normal"
        self._hold_pid = PIDController(self.hold_kp, self.hold_ki, self.hold_kd)
        self.reset()

    def _setup_tank(self) -> None:
        """Initialize differential-drive control and optional odometry."""
        if not isinstance(self.components, dict):
            raise TypeError("smoothdrive_components must be a dictionary")
        try:
            left_motor = self.components["left_motor"]
            right_motor = self.components["right_motor"]
        except KeyError as error:
            raise ValueError(
                "smoothdrive_components must contain 'left_motor' and 'right_motor'"
            ) from error

        if self.max_speed_mps <= 0:
            raise ValueError("smoothdrive_max_speed_mps must be greater than zero")
        track_width = self._convert_distance(self.track_width, self.units, "meters")
        if track_width <= 0:
            raise ValueError("smoothdrive_track_width must be greater than zero")

        self._tank_drive = wpilib.drive.DifferentialDrive(left_motor, right_motor)
        self._tank_kinematics = DifferentialDriveKinematics(track_width)
        self._left_encoder = self.components.get("left_encoder")
        self._right_encoder = self.components.get("right_encoder")
        self._tank_odometry: DifferentialDriveOdometry | None = None
        if self._left_encoder is not None and self._right_encoder is not None:
            self._tank_odometry = DifferentialDriveOdometry(
                self._get_heading(),
                self._get_left_distance(),
                self._get_right_distance(),
            )

    def _setup_swerve(self) -> None:
        """Initialize four-module swerve kinematics and odometry."""
        if not isinstance(self.components, dict):
            raise TypeError("smoothdrive_components must be a dictionary")
        if len(self.module_locations) != 4:
            raise ValueError("smoothdrive_module_locations must contain four locations")
        if self.max_speed_mps <= 0:
            raise ValueError("smoothdrive_max_speed_mps must be greater than zero")
        if self.max_angular_speed_rps <= 0:
            raise ValueError(
                "smoothdrive_max_angular_speed_rps must be greater than zero"
            )
        self._modules = tuple(
            self._create_swerve_module(name)
            for name in ("front_left", "front_right", "back_left", "back_right")
        )
        self._swerve_kinematics = SwerveDrive4Kinematics(*self.module_locations)
        self._swerve_odometry = SwerveDrive4Odometry(
            self._swerve_kinematics,
            self._get_heading(),
            self._get_module_positions(),
        )

    def _create_swerve_module(self, name: str) -> SwerveModule:
        """Create and initialize one module from the injected component map."""
        if not isinstance(self.components, dict):
            raise TypeError("smoothdrive_components must be a dictionary")

        required_suffixes = (
            "drive_motor",
            "steering_motor",
            "drive_encoder",
            "steering_encoder",
            "steering_offset_degrees",
            "drive_pid",
            "steering_pid",
        )
        missing = [
            f"{name}_{suffix}"
            for suffix in required_suffixes
            if f"{name}_{suffix}" not in self.components
        ]
        if missing:
            raise ValueError(
                f"smoothdrive_components is missing required swerve entries: "
                f"{', '.join(missing)}"
            )

        module = SwerveModule()
        module.drive_motor = self.components[f"{name}_drive_motor"]
        module.steering_motor = self.components[f"{name}_steering_motor"]
        module.drive_encoder = self.components[f"{name}_drive_encoder"]
        module.steering_encoder = self.components[f"{name}_steering_encoder"]
        module.steering_offset_degrees = self.components[
            f"{name}_steering_offset_degrees"
        ]
        module.drive_pid = self.components[f"{name}_drive_pid"]
        module.steering_pid = self.components[f"{name}_steering_pid"]
        module.setup()
        return module

    @staticmethod
    def _convert_distance(distance: float, from_units: str, to_units: str) -> float:
        """Convert a distance between meters, inches, or feet."""
        source = from_units.strip().lower()
        target = to_units.strip().lower()

        if source in ("m", "meter", "meters"):
            meters = distance
        elif source in ("in", "inch", "inches"):
            meters = wpimath_units.inchesToMeters(distance)
        elif source in ("ft", "foot", "feet"):
            meters = wpimath_units.feetToMeters(distance)
        else:
            raise ValueError(
                f"Unsupported distance unit {from_units!r}; use meters, inches, or feet"
            )

        if target in ("m", "meter", "meters"):
            return meters
        if target in ("in", "inch", "inches"):
            return wpimath_units.metersToInches(meters)
        if target in ("ft", "foot", "feet"):
            return wpimath_units.metersToFeet(meters)
        raise ValueError(
            f"Unsupported distance unit {to_units!r}; use meters, inches, or feet"
        )

    def _get_heading(self) -> Rotation2d:
        """Return the gyro heading, including an optional simulation override."""
        if self._type == "tank" and self._tank_simulation_readings is not None:
            return self._tank_simulation_readings[2]
        if self._type == "swerve" and self._swerve_simulation_heading is not None:
            return self._swerve_simulation_heading
        return self.gyro.rotation

    def _get_left_distance(self) -> float:
        """Return the left encoder distance in meters."""
        if self._tank_simulation_readings is not None:
            distance = self._tank_simulation_readings[0]
        else:
            if self._left_encoder is None:
                raise RuntimeError("Tank odometry requires a left encoder")
            distance = self._left_encoder.getDistance()
        return self._convert_distance(distance, self.units, "meters")

    def _get_right_distance(self) -> float:
        """Return the right encoder distance in meters."""
        if self._tank_simulation_readings is not None:
            distance = self._tank_simulation_readings[1]
        else:
            if self._right_encoder is None:
                raise RuntimeError("Tank odometry requires a right encoder")
            distance = self._right_encoder.getDistance()
        return self._convert_distance(distance, self.units, "meters")

    def _get_module_positions(
        self,
    ) -> tuple[
        SwerveModulePosition,
        SwerveModulePosition,
        SwerveModulePosition,
        SwerveModulePosition,
    ]:
        """Read module positions in front-left, front-right, back-left, back-right order."""
        return tuple(module.get_position() for module in self._modules)

    def _execute_tank(self) -> None:
        """Convert chassis speeds to bounded left and right motor outputs."""
        wheel_speeds = self._tank_kinematics.toWheelSpeeds(self.speeds)
        max_wheel_speed = max(abs(wheel_speeds.left), abs(wheel_speeds.right))
        scale = max(1.0, max_wheel_speed / self.max_speed_mps)
        self._tank_drive.tankDrive(
            wheel_speeds.left / (self.max_speed_mps * scale),
            wheel_speeds.right / (self.max_speed_mps * scale),
            squareInputs=False,
        )
        if self._tank_odometry is not None:
            self.pose = self._tank_odometry.update(
                self._get_heading(),
                self._get_left_distance(),
                self._get_right_distance(),
            )

    def _execute_swerve(self) -> None:
        """Calculate module targets from chassis speeds and update odometry."""
        states = self._swerve_kinematics.toSwerveModuleStates(self.speeds)
        states = self._swerve_kinematics.desaturateWheelSpeeds(
            states, self.max_speed_mps
        )
        for module, state in zip(self._modules, states, strict=True):
            module.set_desired_state(state)
            module.execute()
        self.pose = self._swerve_odometry.update(
            self._get_heading(),
            self._get_module_positions(),
        )

    # -- Public API --------------------------------------------------------

    def reset(self) -> None:
        """Stop the output and forget any heading target.

        Call this from ``teleopInit`` (after ``gyro.reset()``) and any time
        you re-zero the gyro, so an old target can't linger.
        """
        self._vx = 0.0
        self._vy = 0.0
        self._omega = 0.0
        self._heading_target = None
        self._settle_elapsed = 0.0
        self._heading_error_rad = 0.0
        self._hold_pid.reset()
        self.speeds = ChassisSpeeds()
        self._stop_requested = False

    def set_mode(self, mode: str) -> None:
        """Choose "normal", "boost", or "precision" for the next loop."""
        cleaned = mode.strip().lower()
        valid_modes = ("normal", "boost", "precision")
        if cleaned not in valid_modes:
            raise ValueError(f"Unknown mode {mode!r}; valid options: {valid_modes}")
        self._mode = cleaned

    def drive(self, fwd: float, rot: float, strafe: float = 0.0) -> None:
        """Provide raw stick values, each from -1 to 1.

        Forward is positive, left is positive, and counterclockwise is
        positive. Call this every loop from ``teleopPeriodic``.
        """
        self.fwd_input = fwd
        self.rot_input = rot
        self.strafe_input = strafe
        self._stop_requested = False

    @property
    def mode(self) -> str:
        """Return the current driving mode."""
        return self._mode

    @property
    def holding_heading(self) -> bool:
        """Return whether a heading target is currently being held."""
        return self._heading_target is not None

    # -- Feedback for dashboards ------------------------------------------

    @feedback
    def mode_name(self) -> str:
        """Show the current drive mode."""
        return self._mode

    @feedback
    def holding(self) -> bool:
        """Show whether heading hold is active."""
        return self.holding_heading

    @feedback
    def heading_target_degrees(self) -> float:
        """Show the heading target, or NaN when there is none."""
        if self._heading_target is None:
            return math.nan
        return self._heading_target.degrees()

    @feedback
    def heading_error_degrees(self) -> float:
        """Show the heading error while holding."""
        return math.degrees(self._heading_error_rad)

    @feedback
    def odometry_enabled(self) -> bool:
        """Show whether the selected drive has configured odometry."""
        if self._type == "tank":
            return self._tank_odometry is not None
        return True

    @feedback
    def pose_x_meters(self) -> float:
        """Show the estimated robot X position in meters."""
        return self.pose.X()

    @feedback
    def pose_y_meters(self) -> float:
        """Show the estimated robot Y position in meters."""
        return self.pose.Y()

    # -- Internals ---------------------------------------------------------

    def _mode_limits(self) -> tuple[float, float, float]:
        """Return (max speed, max rotation, slew scale) for the current mode."""
        if self._mode == "boost":
            return (self.max_speed_boost, self.max_rot_boost, self.boost_slew_scale)
        if self._mode == "precision":
            return (
                self.max_speed_precision,
                self.max_rot_precision,
                self.precision_slew_scale,
            )
        return (self.max_speed_normal, self.max_rot_normal, 1.0)

    def _shape_translation(self) -> tuple[float, float]:
        """Deadband and curve the translation stick as one vector.

        The deadband is applied to the vector's length, so pushing the stick
        diagonally doesn't change where the dead zone ends.
        """
        magnitude = math.hypot(self.fwd_input, self.strafe_input)
        if self._type == "tank":
            magnitude = abs(self.fwd_input)
        if magnitude < 1e-9:
            return (0.0, 0.0)
        shaped = self.apply_curve(
            applyDeadband(min(magnitude, 1.0), self.deadband), self.translation_curve
        )
        if self._type == "tank":
            return (math.copysign(shaped, self.fwd_input), 0.0)
        scale = shaped / magnitude  # keeps direction, even past a 1.0 corner
        return (self.fwd_input * scale, self.strafe_input * scale)

    def _shape_rotation(self) -> float:
        """Deadband and curve the rotation stick."""
        return self.apply_curve(
            applyDeadband(max(-1.0, min(1.0, self.rot_input)), self.deadband),
            self.rotation_curve,
        )

    def _update_heading_hold(
        self, rotating: bool, translating: bool, dt: float, max_rot: float
    ) -> float | None:
        """Run the heading hold rules.

        Returns a rotation command in rad/s when the hold is steering, or
        None when the driver (or a stopped robot) is in control.
        """
        gyro_ok = self.gyro.connected()

        if rotating or not translating or not gyro_ok or not self.heading_hold_enabled:
            self._heading_target = None
            self._settle_elapsed = 0.0
            self._heading_error_rad = 0.0
            return None

        if self._heading_target is None:
            # Wait until the robot has really stopped turning before locking
            # on, otherwise we would grab a heading mid-turn and overshoot.
            if abs(self.gyro.rate_dps) < self.settle_rate_dps:
                self._settle_elapsed += dt
            else:
                self._settle_elapsed = 0.0

            if self._settle_elapsed < self.settle_time:
                return None

            self._heading_target = self.gyro.rotation
            self._hold_pid.reset()

        # Rotation2d subtraction wraps to +/- pi, so no continuous-input
        # PID is needed. Error is the shortest turn from heading to target.
        error = (self._heading_target - self.gyro.rotation).radians()
        self._heading_error_rad = error
        self._hold_pid.setP(self.hold_kp)
        self._hold_pid.setD(self.hold_kd)
        # PIDController computes (setpoint - measurement), so measurement 0
        # and setpoint = error gives a command that turns toward the target.
        correction = self._hold_pid.calculate(0.0, error)
        limit = max_rot * self.hold_max_fraction
        return max(-limit, min(limit, correction))

    # -- MagicBot calls this every loop -----------------------------------

    def execute(self) -> None:
        """Compute smoothed chassis speeds and command the selected drive."""
        if self._stop_requested:
            if self._type == "tank":
                self._tank_drive.stopMotor()
            else:
                for module in self._modules:
                    module.stop()
                self.pose = self._swerve_odometry.update(
                    self._get_heading(),
                    self._get_module_positions(),
                )
            return

        dt = self.control_loop_wait_time
        max_speed, max_rot, slew_scale = self._mode_limits()
        if self._type == "swerve":
            max_rot = min(max_rot, self.max_angular_speed_rps)

        # 1-3. Shape the sticks and scale to real units.
        tx, ty = self._shape_translation()
        target_vx = tx * max_speed
        target_vy = ty * max_speed
        rot_shaped = self._shape_rotation()
        target_omega = rot_shaped * max_rot

        rotating = rot_shaped != 0.0
        translating = (tx != 0.0) or (ty != 0.0)

        # 4a. Slew translation as a vector.
        self._vx, self._vy = self.slew_vector(
            (self._vx, self._vy),
            (target_vx, target_vy),
            self.translation_accel * slew_scale,
            self.translation_decel * slew_scale,
            dt,
        )

        # 5. Heading hold may take over rotation.
        hold_omega = self._update_heading_hold(rotating, translating, dt, max_rot)

        if hold_omega is not None:
            # The PID output is already a smooth, clamped command, and
            # running it through a slew limiter would add lag that can make
            # the hold oscillate. Just keep the limiter's state in sync so
            # handing control back to the driver is smooth.
            self._omega = hold_omega
        else:
            # 4b. Slew rotation (also ramps down after the hold lets go).
            self._omega = self.slew_scalar(
                self._omega,
                target_omega,
                self.rotation_accel * slew_scale,
                self.rotation_decel * slew_scale,
                dt,
            )

        self.speeds = ChassisSpeeds(self._vx, self._vy, self._omega)
        if self._type == "tank":
            self._execute_tank()
        else:
            self._execute_swerve()

    def reset_odometry(self, pose: Pose2d | None = None) -> None:
        """Reset the estimated position using the selected drivetrain sensors."""
        if pose is None:
            pose = Pose2d()
        if self._type == "tank":
            if self._tank_odometry is None:
                raise RuntimeError("Tank odometry requires two encoders")
            self._tank_odometry.resetPosition(
                self._get_heading(),
                self._get_left_distance(),
                self._get_right_distance(),
                pose,
            )
        else:
            self._swerve_odometry.resetPosition(
                self._get_heading(),
                self._get_module_positions(),
                pose,
            )
        self.pose = pose

    def get_pose(self, units: str = "meters") -> Pose2d:
        """Return the estimated pose, converting X and Y to the requested units."""
        return Pose2d(
            self._convert_distance(self.pose.X(), "meters", units),
            self._convert_distance(self.pose.Y(), "meters", units),
            self.pose.rotation(),
        )

    @overload
    def set_simulation_readings(
        self, left_distance: float, right_distance: float, heading: Rotation2d
    ) -> None: ...

    @overload
    def set_simulation_readings(
        self,
        heading: Rotation2d,
        module_readings: tuple[
            tuple[float, float, Rotation2d],
            tuple[float, float, Rotation2d],
            tuple[float, float, Rotation2d],
            tuple[float, float, Rotation2d],
        ],
    ) -> None: ...

    def set_simulation_readings(
        self,
        first: float | Rotation2d,
        second: float
        | tuple[
            tuple[float, float, Rotation2d],
            tuple[float, float, Rotation2d],
            tuple[float, float, Rotation2d],
            tuple[float, float, Rotation2d],
        ],
        third: Rotation2d | None = None,
    ) -> None:
        """Set simulated sensor readings using the selected drive's format."""
        if not self._is_simulation:
            raise RuntimeError("Simulation readings require a simulated robot")

        if self._type == "tank":
            if (
                not isinstance(first, (int, float))
                or not isinstance(second, (int, float))
                or not isinstance(third, Rotation2d)
            ):
                raise TypeError(
                    "Tank simulation readings require left distance, right distance, "
                    "and heading"
                )
            if self._tank_odometry is None:
                raise RuntimeError("Tank simulation readings require odometry sensors")
            self._tank_simulation_readings = (first, second, third)
            return

        if not isinstance(first, Rotation2d) or not isinstance(second, tuple):
            raise TypeError(
                "Swerve simulation readings require heading and four module readings"
            )
        if len(second) != 4:
            raise ValueError("Swerve simulation readings must include all four modules")
        self._swerve_simulation_heading = first
        for module, reading in zip(self._modules, second, strict=True):
            module.set_simulation_readings(*reading)

    def reset_encoders(self) -> None:
        """Reset tank encoders when they are configured."""
        if self._type != "tank":
            raise RuntimeError("Encoder reset is only available for tank drive")
        if self._left_encoder is not None:
            self._left_encoder.reset()
        if self._right_encoder is not None:
            self._right_encoder.reset()

    def stop(self) -> None:
        """Reset smoothed commands and stop the selected drivetrain."""
        self.reset()
        self._stop_requested = True
        if self._type == "tank":
            self._tank_drive.stopMotor()
        else:
            for module in self._modules:
                module.stop()
