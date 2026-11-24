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

Usage in a RobotPy MagicBot project. Configure ``drivetrain_config`` with the
drivetrain settings in ``constants.py`` and declare one ``SmoothDrive``
component::

    import constants
    from components.gyro import Gyro
    from components.smoothdrive import SmoothDrive

    class Robot(MagicRobot):
        gyro: Gyro
        drivetrain: SmoothDrive

        def createObjects(self):
            self.drivetrain_config = constants.DRIVETRAIN_CONFIG
            self.drivetrain_components = {
                # Configure motor, encoder, offset, and PID keys for all modules.
            }

        def teleopPeriodic(self):
            self.drivetrain.drive(
                fwd=-self.stick.getLeftY(),
                strafe=-self.stick.getLeftX(),
                rot=-self.stick.getRightX(),
            )

For tank, configure ``drivetrain_components`` with ``left_motor`` and
``right_motor``. Set the track width and speed limits in
``DRIVETRAIN_CONFIG``. Encoders are optional and enable odometry when both are
provided. Tank drive ignores strafe.

For swerve, configure ``module_locations`` in ``DRIVETRAIN_CONFIG`` as four
``(x, y)`` coordinate pairs in front-left, front-right, back-left, back-right
order. Set speed limits in that same dictionary. Supply each module's
hardware in ``drivetrain_components`` using keys of the form
``<module>_drive_motor``, ``<module>_steering_motor``,
``<module>_drive_encoder``, ``<module>_steering_encoder``,
``<module>_steering_offset_degrees``, ``<module>_drive_pid``, and
``<module>_steering_pid``. Replace ``<module>`` with ``front_left``,
``front_right``, ``back_left``, or ``back_right``.

All drivetrain settings are configured in ``constants.py`` and passed through
``drivetrain_config``. Speeds are in m/s and rad/s.

``control_loop_wait_time`` is the control-loop period in seconds.
"""

from __future__ import annotations

import math
from typing import Any, overload

import wpilib
from magicbot import feedback, will_reset_to
from wpimath import (
    ChassisVelocities,
    DifferentialDriveKinematics,
    DifferentialDriveOdometry,
    PIDController,
    Pose2d,
    Rotation2d,
    SwerveDrive4Kinematics,
    SwerveDrive4Odometry,
    SwerveModulePosition,
    Translation2d,
    apply_deadband,
)
from wpimath import units as wpimath_units

from .gyro import Gyro
from .swervemodule import SwerveModule


class SmoothDrive:
    """Smooth driver input and control a tank or swerve drivetrain."""

    # MagicBot injects only these drivetrain dependencies.
    config: dict[str, Any]
    gyro: Gyro
    components: dict[str, Any]

    # Inputs, cleared to 0 every loop so stale values can't stick
    fwd_input: float = will_reset_to(0.0)
    strafe_input: float = will_reset_to(0.0)
    rot_input: float = will_reset_to(0.0)

    # -- Initialization ----------------------------------------------------
    def setup(self) -> None:
        """Validate and initialize the selected drivetrain and controls."""
        if not isinstance(self.config, dict):
            raise TypeError("smoothdrive_config must be a dictionary")
        required_config = (
            "type",
            "max_speed_mps",
            "max_rot_rps",
            "max_speed",
            "max_rot",
            "slew_scale",
            "track_width",
            "units",
            "module_locations",
            "deadband",
            "translation_curve",
            "rotation_curve",
            "translation_accel",
            "translation_decel",
            "rotation_accel",
            "rotation_decel",
            "heading_hold_enabled",
            "hold_kp",
            "hold_ki",
            "hold_kd",
            "settle_rate_dps",
            "settle_time",
            "hold_max_fraction",
            "control_loop_wait_time",
        )
        missing_config = [key for key in required_config if key not in self.config]
        if missing_config:
            raise ValueError(
                f"smoothdrive_config is missing required keys: "
                f"{', '.join(missing_config)}"
            )

        self._type = self.config["type"].strip().lower()
        if self._type not in ("tank", "swerve"):
            raise ValueError(
                f"Unknown smoothdrive_config type {self.config['type']!r}; "
                "use 'tank' or 'swerve'"
            )
        self._max_speed_mps = self.config["max_speed_mps"]
        self._max_angular_speed_rps = self.config["max_rot_rps"]
        self._max_speed = self.config["max_speed"]
        self._max_rot = self.config["max_rot"]
        self._slew_scale = self.config["slew_scale"]
        self._track_width = self.config["track_width"]
        self._units = self.config["units"]
        self._module_locations = tuple(
            Translation2d(*location) for location in self.config["module_locations"]
        )
        self._deadband = self.config["deadband"]
        self._translation_curve = self.config["translation_curve"]
        self._rotation_curve = self.config["rotation_curve"]
        self._translation_accel = self.config["translation_accel"]
        self._translation_decel = self.config["translation_decel"]
        self._rotation_accel = self.config["rotation_accel"]
        self._rotation_decel = self.config["rotation_decel"]
        self._heading_hold_enabled = self.config["heading_hold_enabled"]
        self._hold_kp = self.config["hold_kp"]
        self._hold_ki = self.config["hold_ki"]
        self._hold_kd = self.config["hold_kd"]
        self._settle_rate_dps = self.config["settle_rate_dps"]
        self._settle_time = self.config["settle_time"]
        self._hold_max_fraction = self.config["hold_max_fraction"]
        self._control_loop_wait_time = self.config["control_loop_wait_time"]

        valid_modes = ("normal", "boost", "precision")
        for name, limits in (
            ("max_speed", self._max_speed),
            ("max_rot", self._max_rot),
            ("slew_scale", self._slew_scale),
        ):
            if not isinstance(limits, dict):
                raise TypeError(f"smoothdrive_{name} must be a dictionary")
            missing = [mode for mode in valid_modes if mode not in limits]
            if missing:
                raise ValueError(f"smoothdrive_{name} must contain keys: {valid_modes}")
            if any(limits[mode] <= 0 for mode in valid_modes):
                raise ValueError(
                    f"All smoothdrive_{name} values must be greater than zero"
                )

        self._is_simulation = wpilib.RobotBase.is_simulation()
        self.pose = Pose2d()
        self._tank_simulation_readings: tuple[float, float, Rotation2d] | None = None
        self._swerve_simulation_heading: Rotation2d | None = None
        self._stop_requested = False

        if self._type == "tank":
            self._setup_tank()
        else:
            self._setup_swerve()

        self._mode = "normal"
        self._hold_pid = PIDController(self._hold_kp, self._hold_ki, self._hold_kd)
        self.reset()

    # -- Drivetrain setup --------------------------------------------------
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

        if self._max_speed_mps <= 0:
            raise ValueError("smoothdrive_max_speed_mps must be greater than zero")
        track_width = self._convert_distance(self._track_width, self._units, "meters")
        if track_width <= 0:
            raise ValueError("smoothdrive_track_width must be greater than zero")

        self._tank_drive = wpilib.DifferentialDrive(left_motor, right_motor)
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
        if len(self._module_locations) != 4:
            raise ValueError(
                "smoothdrive_config module_locations must contain four locations"
            )
        if self._max_speed_mps <= 0:
            raise ValueError("smoothdrive_max_speed_mps must be greater than zero")
        if self._max_angular_speed_rps <= 0:
            raise ValueError(
                "smoothdrive_max_angular_speed_rps must be greater than zero"
            )
        self._modules = tuple(
            self._create_swerve_module(name)
            for name in ("front_left", "front_right", "back_left", "back_right")
        )
        self._swerve_kinematics = SwerveDrive4Kinematics(*self._module_locations)
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

    # -- Sensor and geometry helpers --------------------------------------
    @staticmethod
    def _convert_distance(distance: float, from_units: str, to_units: str) -> float:
        """Convert a distance between meters, inches, or feet."""
        source = from_units.strip().lower()
        target = to_units.strip().lower()

        if source in ("m", "meter", "meters"):
            meters = distance
        elif source in ("in", "inch", "inches"):
            meters = wpimath_units.inches_to_meters(distance)
        elif source in ("ft", "foot", "feet"):
            meters = wpimath_units.feet_to_meters(distance)
        else:
            raise ValueError(
                f"Unsupported distance unit {from_units!r}; use meters, inches, or feet"
            )

        if target in ("m", "meter", "meters"):
            return meters
        if target in ("in", "inch", "inches"):
            return wpimath_units.meters_to_inches(meters)
        if target in ("ft", "foot", "feet"):
            return wpimath_units.meters_to_feet(meters)
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
            distance = self._left_encoder.get_distance()
        return self._convert_distance(distance, self._units, "meters")

    def _get_right_distance(self) -> float:
        """Return the right encoder distance in meters."""
        if self._tank_simulation_readings is not None:
            distance = self._tank_simulation_readings[1]
        else:
            if self._right_encoder is None:
                raise RuntimeError("Tank odometry requires a right encoder")
            distance = self._right_encoder.get_distance()
        return self._convert_distance(distance, self._units, "meters")

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

    # -- Hardware output --------------------------------------------------
    def _execute_tank(self) -> None:
        """Convert chassis speeds to bounded left and right motor outputs."""
        wheel_speeds = self._tank_kinematics.to_wheel_velocities(self.speeds)
        max_wheel_speed = max(abs(wheel_speeds.left), abs(wheel_speeds.right))
        scale = max(1.0, max_wheel_speed / self._max_speed_mps)
        self._tank_drive.tank_drive(
            wheel_speeds.left / (self._max_speed_mps * scale),
            wheel_speeds.right / (self._max_speed_mps * scale),
            False,
        )
        if self._tank_odometry is not None:
            self.pose = self._tank_odometry.update(
                self._get_heading(),
                self._get_left_distance(),
                self._get_right_distance(),
            )

    def _execute_swerve(self) -> None:
        """Calculate module targets from chassis speeds and update odometry."""
        states = self._swerve_kinematics.to_swerve_module_velocities(self.speeds)
        states = self._swerve_kinematics.desaturate_wheel_velocities(
            states, self._max_speed_mps
        )
        for module, state in zip(self._modules, states, strict=True):
            module.set_desired_state(state)
            module.execute()
        self.pose = self._swerve_odometry.update(
            self._get_heading(),
            self._get_module_positions(),
        )

    # -- Driver controls ---------------------------------------------------

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
        self.speeds = ChassisVelocities()
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

    # -- Dashboard feedback -----------------------------------------------

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
        return self.pose.x

    @feedback
    def pose_y_meters(self) -> float:
        """Show the estimated robot Y position in meters."""
        return self.pose.y

    @feedback
    def velocity(self) -> float:
        """Show the robot's current translational velocity in meters per second."""
        return math.hypot(self._vx, self._vy)

    # -- Input and heading calculations -----------------------------------
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

    def _mode_limits(self) -> tuple[float, float, float]:
        """Return (max speed, max rotation, slew scale) for the current mode."""
        return (
            self._max_speed[self._mode],
            self._max_rot[self._mode],
            self._slew_scale[self._mode],
        )

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
            apply_deadband(min(magnitude, 1.0), self._deadband),
            self._translation_curve,
        )
        if self._type == "tank":
            return (math.copysign(shaped, self.fwd_input), 0.0)
        scale = shaped / magnitude  # keeps direction, even past a 1.0 corner
        return (self.fwd_input * scale, self.strafe_input * scale)

    def _shape_rotation(self) -> float:
        """Deadband and curve the rotation stick."""
        return self.apply_curve(
            apply_deadband(max(-1.0, min(1.0, self.rot_input)), self._deadband),
            self._rotation_curve,
        )

    def _update_heading_hold(
        self, rotating: bool, translating: bool, dt: float, max_rot: float
    ) -> float | None:
        """Run the heading hold rules.

        Returns a rotation command in rad/s when the hold is steering, or
        None when the driver (or a stopped robot) is in control.
        """
        gyro_ok = self.gyro.connected()

        if rotating or not translating or not gyro_ok or not self._heading_hold_enabled:
            self._heading_target = None
            self._settle_elapsed = 0.0
            self._heading_error_rad = 0.0
            return None

        if self._heading_target is None:
            # Wait until the robot has really stopped turning before locking
            # on, otherwise we would grab a heading mid-turn and overshoot.
            if abs(self.gyro.rate_dps) < self._settle_rate_dps:
                self._settle_elapsed += dt
            else:
                self._settle_elapsed = 0.0

            if self._settle_elapsed < self._settle_time:
                return None

            self._heading_target = self.gyro.rotation
            self._hold_pid.reset()

        # Rotation2d subtraction wraps to +/- pi, so no continuous-input
        # PID is needed. Error is the shortest turn from heading to target.
        error = (self._heading_target - self.gyro.rotation).radians()
        self._heading_error_rad = error
        self._hold_pid.set_p(self._hold_kp)
        self._hold_pid.set_d(self._hold_kd)
        # PIDController computes (setpoint - measurement), so measurement 0
        # and setpoint = error gives a command that turns toward the target.
        correction = self._hold_pid.calculate(0.0, error)
        limit = max_rot * self._hold_max_fraction
        return max(-limit, min(limit, correction))

    # -- MagicBot control loop --------------------------------------------

    def execute(self) -> None:
        """Compute smoothed chassis speeds and command the selected drive."""
        if self._stop_requested:
            if self._type == "tank":
                self._tank_drive.stop_motor()
            else:
                for module in self._modules:
                    module.stop()
                self.pose = self._swerve_odometry.update(
                    self._get_heading(),
                    self._get_module_positions(),
                )
            return

        dt = self._control_loop_wait_time
        max_speed, max_rot, slew_scale = self._mode_limits()
        if self._type == "swerve":
            max_rot = min(max_rot, self._max_angular_speed_rps)

        # Shape stick input and scale it to real units.
        tx, ty = self._shape_translation()
        target_vx = tx * max_speed
        target_vy = ty * max_speed
        rot_shaped = self._shape_rotation()
        target_omega = rot_shaped * max_rot

        rotating = rot_shaped != 0.0
        translating = (tx != 0.0) or (ty != 0.0)

        # Smooth translation as a vector.
        self._vx, self._vy = self.slew_vector(
            (self._vx, self._vy),
            (target_vx, target_vy),
            self._translation_accel * slew_scale,
            self._translation_decel * slew_scale,
            dt,
        )

        # Heading hold may take over rotation.
        hold_omega = self._update_heading_hold(rotating, translating, dt, max_rot)

        if hold_omega is not None:
            # The PID output is already a smooth, clamped command, and
            # running it through a slew limiter would add lag that can make
            # the hold oscillate. Just keep the limiter's state in sync so
            # handing control back to the driver is smooth.
            self._omega = hold_omega
        else:
            # Smooth rotation, also ramping down after heading hold lets go.
            self._omega = self.slew_scalar(
                self._omega,
                target_omega,
                self._rotation_accel * slew_scale,
                self._rotation_decel * slew_scale,
                dt,
            )

        self.speeds = ChassisVelocities(self._vx, self._vy, self._omega)
        if self._type == "tank":
            self._execute_tank()
        else:
            self._execute_swerve()

    # -- Odometry and simulation API --------------------------------------
    def reset_odometry(self, pose: Pose2d | None = None) -> None:
        """Reset the estimated position using the selected drivetrain sensors."""
        if pose is None:
            pose = Pose2d()
        if self._type == "tank":
            if self._tank_odometry is None:
                raise RuntimeError("Tank odometry requires two encoders")
            self._tank_odometry.reset_position(
                self._get_heading(),
                self._get_left_distance(),
                self._get_right_distance(),
                pose,
            )
        else:
            self._swerve_odometry.reset_position(
                self._get_heading(),
                self._get_module_positions(),
                pose,
            )
        self.pose = pose

    def get_pose(self, units: str = "meters") -> Pose2d:
        """Return the estimated pose, converting X and Y to the requested units."""
        return Pose2d(
            self._convert_distance(self.pose.x, "meters", units),
            self._convert_distance(self.pose.y, "meters", units),
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
            self._tank_drive.stop_motor()
        else:
            for module in self._modules:
                module.stop()
