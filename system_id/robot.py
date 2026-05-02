#!/usr/bin/env python3
"""
XRP Robot - Tank Drive with System Identification
==================================================
Hardware:
  - 2x XRP motors with encoders (left / right)
  - XRP onboard gyro  (xrp.XRPGyro)
  - 4x AA batteries  (~6 V nominal, ~5.2 V loaded)
  - Xbox controller (USB, port 0)

Modes
-----
  Teleop  : Tank drive via Xbox left-Y / right-Y sticks.
  SysId   : Entering Test mode automatically runs all 4 characterisation
            routines in sequence (quasi-fwd → quasi-rev → dyn-fwd → dyn-rev)
            with a short coast/pause between each one.
            Data is logged via DataLogManager (.wpilog file) and
            can be opened in the WPILib SysId Analyzer.

NOTE on battery voltage
-----------------------
  The XRP runs on 4 AA batteries.  RobotController.getBatteryVoltage()
  always returns 12 V on the XRP because it is not wired to the battery.
  We therefore use a fixed BATTERY_VOLTAGE constant.  Fresh alkalines give
  ~6 V; under load / partially depleted NiMH cells sit closer to 4.8 V.
  Adjust BATTERY_VOLTAGE to match your pack.

SysId Auto-Sequence (Test mode)
---------------------------------
  Entering Test mode starts the sequence automatically:
    1. quasi-fwd   (quasistatic ramp forward)
    2. quasi-rev   (quasistatic ramp reverse)
    3. dyn-fwd     (dynamic step forward)
    4. dyn-rev     (dynamic step reverse)
  Each routine runs for SYSID_ROUTINE_DURATION seconds, then the robot
  coasts for SYSID_COAST_DURATION seconds before the next routine begins.
  Back button cancels at any time.
"""

import math
import wpilib
import wpilib.drive
from xrp import XRPMotor, XRPGyro
from wpimath.geometry import Rotation2d
from wpilib import DataLogManager
from wpiutil.log import DoubleLogEntry, StringLogEntry
import os

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"

# ---------------------------------------------------------------------------
# Constants – tune these for your specific robot
# ---------------------------------------------------------------------------

# Nominal battery voltage for the 4×AA pack.
# RobotController.getBatteryVoltage() always returns 12 V on the XRP,
# so we use a fixed value here.  Typical values:
#   Fresh alkaline 4×AA  → ~6.0 V
#   NiMH 4×AA (charged)  → ~5.0 V
#   NiMH under load      → ~4.8 V
BATTERY_VOLTAGE: float = 4.8  # V  ← adjust to match your pack

# SysId quasistatic ramp rate (volts per second)
SYSID_QUASI_RAMP_RATE: float = 0.20  # V/s  (lower = gentler ramp for small robot)

# SysId dynamic step voltage
SYSID_DYNAMIC_STEP_VOLTAGE: float = 3.0  # V  (kept modest for a small 6 V robot)

# How long each SysId routine runs before moving to the next (seconds).
# For quasi routines this determines maximum voltage reached:
#   max_V = SYSID_QUASI_RAMP_RATE × SYSID_ROUTINE_DURATION
#         = 0.20 × 10 = 2.0 V  (well within the 4.8 V pack)
SYSID_ROUTINE_DURATION: float = 10.0  # s

# Coast/pause time between routines so the robot stops before reversing.
SYSID_COAST_DURATION: float = 2.0  # s

# Encoder distance per pulse (metres).
# XRP wheel diameter ≈ 60 mm, 585 counts per revolution
# (12 CPR motor encoder × 48.75 : 1 gear ratio = 585 CPR at wheel).
WHEEL_DIAMETER_M: float = 0.060
ENCODER_CPR: float = 585.0
DISTANCE_PER_COUNT: float = (math.pi * WHEEL_DIAMETER_M) / ENCODER_CPR

# Drivetrain track width (centre-to-centre of wheels, metres)
TRACK_WIDTH_M: float = 0.155

# Joystick deadband
DEADBAND: float = 0.08

# Maximum voltage used during teleop
MAX_VOLTAGE: float = BATTERY_VOLTAGE * 0.95  # V  (leave headroom on a battery pack)

# Ordered list of routines the auto-sequencer runs through.
SYSID_SEQUENCE = ["quasi-fwd", "quasi-rev", "dyn-fwd", "dyn-rev"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def apply_deadband(value: float, band: float = DEADBAND) -> float:
    """Return 0 if |value| < band, otherwise rescale to fill the full range."""
    if abs(value) < band:
        return 0.0
    return (value - math.copysign(band, value)) / (1.0 - band)


def volts_to_speed(volts: float) -> float:
    """Convert a voltage command to a [-1, 1] motor set() value."""
    return max(-1.0, min(1.0, volts / BATTERY_VOLTAGE))


# ---------------------------------------------------------------------------
# Robot class
# ---------------------------------------------------------------------------


class MyRobot(wpilib.TimedRobot):
    """Main robot class – inherits from TimedRobot (20 ms periodic loop)."""

    # ------------------------------------------------------------------
    # robotInit
    # ------------------------------------------------------------------
    def robotInit(self) -> None:
        # ---- Motors ------------------------------------------------------
        # XRP left motor → channel 0, right motor → channel 1.
        # The right side is physically mirrored, so invert it.
        self.left_motor = XRPMotor(0)
        self.right_motor = XRPMotor(1)
        self.right_motor.setInverted(True)

        # ---- Encoders ----------------------------------------------------
        # XRP encoder GPIO pin assignments (left: 4/5, right: 6/7).
        self.left_encoder = wpilib.Encoder(4, 5)
        self.right_encoder = wpilib.Encoder(6, 7)

        self.left_encoder.setDistancePerPulse(DISTANCE_PER_COUNT)
        self.right_encoder.setDistancePerPulse(DISTANCE_PER_COUNT)
        # Right encoder counts backwards relative to forward motion.
        self.right_encoder.setReverseDirection(True)

        # ---- Gyro --------------------------------------------------------
        # XRPGyro wraps the onboard IMU.
        # reset()    → zeros the integrated heading
        # getAngle() → cumulative yaw in degrees (Z axis, continuous)
        # getRate()  → yaw rate in degrees per second
        self.gyro = XRPGyro()

        # ---- Differential Drive ------------------------------------------
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.drive.setDeadband(0.0)  # deadband handled manually

        # ---- Xbox Controller ---------------------------------------------
        self.controller = wpilib.XboxController(0)

        # ---- Data Logging ------------------------------------------------
        # Writes a .wpilog file.
        DataLogManager.start()
        self.log = DataLogManager.getLog()

        # SysId log channels (names match WPILib SysId Analyzer expectations)
        self._log_timestamp = DoubleLogEntry(self.log, "/sysid/timestamp")
        self._log_voltage_l = DoubleLogEntry(self.log, "/sysid/left-voltage")
        self._log_voltage_r = DoubleLogEntry(self.log, "/sysid/right-voltage")
        self._log_position_l = DoubleLogEntry(self.log, "/sysid/left-position")
        self._log_position_r = DoubleLogEntry(self.log, "/sysid/right-position")
        self._log_velocity_l = DoubleLogEntry(self.log, "/sysid/left-velocity")
        self._log_velocity_r = DoubleLogEntry(self.log, "/sysid/right-velocity")
        self._log_gyro_angle = DoubleLogEntry(self.log, "/sysid/gyro-angle")
        self._log_gyro_rate = DoubleLogEntry(self.log, "/sysid/gyro-rate")
        self._log_test_state = StringLogEntry(self.log, "/sysid/test-state")

        # ---- SysId runtime state -----------------------------------------
        self._sysid_active: bool = False
        self._sysid_routine: str = "none"
        self._sysid_start_time: float = 0.0

        # Auto-sequencer state
        self._seq_index: int = 0  # which routine in SYSID_SEQUENCE
        self._seq_coasting: bool = False  # True while pausing between routines
        self._seq_coast_start: float = 0.0
        self._seq_done: bool = False  # True after all 4 routines finish

        wpilib.SmartDashboard.putString("SysId State", "Idle")

        self.resetSensors()

    # ------------------------------------------------------------------
    # robotPeriodic  – runs every loop in ALL modes
    # ------------------------------------------------------------------
    def robotPeriodic(self) -> None:
        wpilib.SmartDashboard.putNumber(
            "Left Position (m)", self.left_encoder.getDistance()
        )
        wpilib.SmartDashboard.putNumber(
            "Right Position (m)", self.right_encoder.getDistance()
        )
        wpilib.SmartDashboard.putNumber(
            "Left Velocity (m/s)", self.left_encoder.getRate()
        )
        wpilib.SmartDashboard.putNumber(
            "Right Velocity (m/s)", self.right_encoder.getRate()
        )
        wpilib.SmartDashboard.putNumber("Gyro Angle (deg)", self.getHeadingDegrees())
        wpilib.SmartDashboard.putNumber("Gyro Rate (deg/s)", self.gyro.getRate())
        wpilib.SmartDashboard.putString("SysId Routine", self._sysid_routine)

    # ------------------------------------------------------------------
    # Teleop
    # ------------------------------------------------------------------
    def teleopInit(self) -> None:
        self._stopMotors()
        self._sysid_active = False

    def teleopPeriodic(self) -> None:
        left_speed = apply_deadband(-self.controller.getLeftY())
        right_speed = apply_deadband(-self.controller.getRightY())

        left_volts = left_speed * MAX_VOLTAGE
        right_volts = right_speed * MAX_VOLTAGE
        self._setVoltages(left_volts, right_volts)

    # ------------------------------------------------------------------
    # Test mode  (SysId auto-sequence lives here)
    # ------------------------------------------------------------------
    def testInit(self) -> None:
        """Reset and immediately kick off the auto-sequence."""
        self._stopMotors()
        self.resetSensors()

        # Reset sequencer
        self._seq_index = 0
        self._seq_coasting = False
        self._seq_done = False
        self._sysid_active = False
        self._sysid_routine = "none"
        self._log_test_state.append("none")

        wpilib.SmartDashboard.putString("SysId State", "Starting sequence…")
        print("[SysId] Test mode enabled – auto-sequence will start immediately.")

        # Launch the first routine right away
        self._startSysId(SYSID_SEQUENCE[self._seq_index])

    def testPeriodic(self) -> None:
        """
        Automatic SysId sequencer – no button presses required.

        State machine
        -------------
          RUNNING  → _sysid_active is True; run until SYSID_ROUTINE_DURATION elapses.
          COASTING → motors off for SYSID_COAST_DURATION seconds between routines.
          DONE     → all routines finished; sit idle.

        Back button cancels at any time.
        """
        # Allow emergency cancel via Back button
        if self.controller.getBackButton():
            self._cancelSysId()
            return

        # Nothing left to do
        if self._seq_done:
            return

        now = wpilib.Timer.getFPGATimestamp()

        # ---- Coast phase (pause between routines) -----------------------
        if self._seq_coasting:
            if now - self._seq_coast_start >= SYSID_COAST_DURATION:
                # Coast finished – advance to the next routine
                self._seq_index += 1
                self._seq_coasting = False

                if self._seq_index >= len(SYSID_SEQUENCE):
                    # All routines complete
                    self._seq_done = True
                    self._sysid_routine = "none"
                    self._log_test_state.append("none")
                    wpilib.SmartDashboard.putString(
                        "SysId State", "✓ Sequence complete"
                    )
                    print(
                        "[SysId] All routines complete.  Exit Test mode to save the log."
                    )
                    return

                self._startSysId(SYSID_SEQUENCE[self._seq_index])
            # Still coasting – motors already stopped, just wait
            return

        # ---- Active routine phase ---------------------------------------
        if self._sysid_active:
            elapsed = now - self._sysid_start_time

            if elapsed >= SYSID_ROUTINE_DURATION:
                # Routine time expired – stop and begin coast
                self._stopMotors()
                self._sysid_active = False
                self._seq_coasting = True
                self._seq_coast_start = now
                label = SYSID_SEQUENCE[self._seq_index]
                wpilib.SmartDashboard.putString(
                    "SysId State", f"Coasting after {label}…"
                )
                print(
                    f"[SysId] Routine '{label}' done – coasting {SYSID_COAST_DURATION} s."
                )
            else:
                self._runSysId()

    # ------------------------------------------------------------------
    # Disabled
    # ------------------------------------------------------------------
    def disabledInit(self) -> None:
        self._stopMotors()
        self._sysid_active = False

    # ------------------------------------------------------------------
    # SysId helpers
    # ------------------------------------------------------------------
    def _startSysId(self, routine: str) -> None:
        self.resetSensors()
        self._sysid_routine = routine
        self._sysid_active = True
        self._sysid_start_time = wpilib.Timer.getFPGATimestamp()
        self._log_test_state.append(routine)
        wpilib.SmartDashboard.putString("SysId State", f"RUNNING: {routine}")
        print(f"[SysId] Starting routine: {routine}")

    def _cancelSysId(self) -> None:
        self._stopMotors()
        self._sysid_active = False
        self._seq_coasting = False
        self._seq_done = True  # prevents re-entry without a new testInit
        self._sysid_routine = "none"
        self._log_test_state.append("none")
        wpilib.SmartDashboard.putString("SysId State", "Cancelled / Idle")
        print("[SysId] Routine cancelled.")

    def _runSysId(self) -> None:
        now = wpilib.Timer.getFPGATimestamp()
        elapsed = now - self._sysid_start_time
        sign = 1.0 if "fwd" in self._sysid_routine else -1.0

        if "quasi" in self._sysid_routine:
            # Linearly ramp voltage from 0 V – characterises kS and kV
            applied_voltage = sign * SYSID_QUASI_RAMP_RATE * elapsed
        else:
            # Instant step voltage – characterises kA
            applied_voltage = sign * SYSID_DYNAMIC_STEP_VOLTAGE

        # Clamp to the known battery voltage
        applied_voltage = max(-BATTERY_VOLTAGE, min(BATTERY_VOLTAGE, applied_voltage))

        self._setVoltages(applied_voltage, applied_voltage)

        # Log data for SysId Analyzer
        self._log_timestamp.append(now)
        self._log_voltage_l.append(applied_voltage)
        self._log_voltage_r.append(applied_voltage)
        self._log_position_l.append(self.left_encoder.getDistance())
        self._log_position_r.append(self.right_encoder.getDistance())
        self._log_velocity_l.append(self.left_encoder.getRate())
        self._log_velocity_r.append(self.right_encoder.getRate())
        # SysId Analyzer expects angles/rates in radians
        self._log_gyro_angle.append(math.radians(self.getHeadingDegrees()))
        self._log_gyro_rate.append(math.radians(self.gyro.getRate()))

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _setVoltages(self, left_volts: float, right_volts: float) -> None:
        """Convert voltage commands to [-1, 1] motor values and apply them."""
        self.left_motor.set(volts_to_speed(left_volts))
        self.right_motor.set(volts_to_speed(right_volts))
        self.drive.feed()  # satisfy the motor-safety watchdog

    def _stopMotors(self) -> None:
        self.left_motor.set(0.0)
        self.right_motor.set(0.0)
        self.drive.feed()

    def resetSensors(self) -> None:
        """Zero encoders and gyro – called before every SysId routine."""
        self.left_encoder.reset()
        self.right_encoder.reset()
        self.gyro.reset()  # XRPGyro.reset() zeros the integrated heading

    def getHeadingDegrees(self) -> float:
        """Return current yaw heading in degrees (continuous, zeroed at last reset)."""
        return self.gyro.getAngle()

    def getHeading(self) -> Rotation2d:
        return Rotation2d.fromDegrees(self.getHeadingDegrees())
