"""
OPMODE #5: DRIVETRAIN SYSTEM IDENTIFICATION (SysId)

WHAT IS SYSTEM IDENTIFICATION?
You want feedforward constants for your drivetrain (kS, kV, kA) so you can say "I want this speed"
and have the robot compute the voltage needed. Instead of guessing, you MEASURE them: apply known
voltages, record how the wheels respond, and let the WPILib SysId tool fit a model:

    voltage = kS * sign(velocity) + kV * velocity + kA * acceleration

    kS  voltage just to overcome static friction (get the wheel moving at all)
    kV  extra volts per (meter/second) of steady speed
    kA  extra volts per (meter/second^2) of acceleration

THE FOUR STANDARD TESTS (hold the button to run, release to stop):

    A  Quasistatic FORWARD   slowly ramps voltage up -> reveals kS and kV
    B  Quasistatic REVERSE
    X  Dynamic FORWARD       sudden voltage step      -> reveals kA
    Y  Dynamic REVERSE

Run all four, in any order, in ONE enable session, then open the log in the SysId tool.
Pick a big open space: the XRP will drive a meter or more during a quasistatic test.

WORKFLOW
1. Select "SysId Drivetrain" (a Utility opmode) on the Driver Station and enable.
2. Hold each of the four buttons until the robot stops by itself (see the console messages).
   After a test ends, release the button before starting the next one.
3. Disable. Find the .wpilog file (its folder is printed to the console).
4. Open the WPILib SysId tool, choose "Analyzer", load the log, pick Drivetrain, and set the units
   to meters. It outputs kS, kV and kA.

THE DATA WE LOG (per side): voltage applied, position (m), velocity (m/s). SysIdRoutineLog writes
them in the exact format the analysis tool expects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import wpilib
from wpilib.sysid import State, SysIdRoutineLog

if TYPE_CHECKING:
    from robot import Robot

# ----- Tunable test parameters ------------------------------------------------------------------

# The XRP runs on 4 AA batteries, about 6 V. We convert "volts" to the throttle the motor wants
# (-1..1) by dividing by this. Use fresh batteries so the number is honest!
SUPPLY_VOLTS = 6.0

# Quasistatic: voltage climbs by this many volts per second, until it hits the max, then the test
# ends. A slow ramp keeps acceleration near zero, which is the whole point of "quasistatic".
RAMP_VOLTS_PER_SEC = 0.5
MAX_QUASISTATIC_VOLTS = 3.0

# Dynamic: jump straight to this voltage and watch the wheels accelerate for a short time.
DYNAMIC_STEP_VOLTS = 3.0
DYNAMIC_SECONDS = 2.0


@wpilib.utility(
    name="SysId Drivetrain",
    group="Characterization",
    description="Hold A/B/X/Y for quasistatic fwd/rev and dynamic fwd/rev tests",
)
class SysIdDrivetrain(wpilib.PeriodicOpMode):
    def __init__(self, robot: Robot) -> None:
        super().__init__()
        self.robot = robot

        # One SysIdRoutineLog per full routine. The name must be unique between routines and
        # shows up in the log, e.g. "sysid-test-state-drive".
        self.log = SysIdRoutineLog("drive")

        self.timer = wpilib.Timer()

        # Which test is running right now (State.NONE means idle).
        self.state = State.NONE
        # Becomes True when a test ends on its own; stays True until every button is released
        # so that holding a button doesn't instantly restart the test.
        self.finished = False
        # The voltage currently commanded (signed). Logged every loop.
        self.volts = 0.0

        # Start the data log. SysId tests write their data here, and the SysId desktop tool reads
        # the resulting .wpilog file.
        wpilib.DataLogManager.start()

    def disabled_periodic(self) -> None:
        """Nothing to do while disabled."""

    def start(self) -> None:
        """Runs once on enable. Zero the encoders so positions start at 0 for this session."""
        self.robot.left_encoder.reset()
        self.robot.right_encoder.reset()
        print(f"SysId ready. Log folder: {wpilib.DataLogManager.get_log_dir()}")
        print("Hold A (quasi fwd), B (quasi rev), X (dynamic fwd), or Y (dynamic rev).")

    def periodic(self) -> None:
        wanted = self._read_buttons()

        # Release-to-rearm: once a test finishes, ignore buttons until all are released.
        if wanted == State.NONE:
            self.finished = False
        elif self.finished:
            wanted = State.NONE

        # A different button (or release) means a new test begins or the current one stops.
        if wanted != self.state:
            self.state = wanted
            self.timer.restart()  # each test's clock starts when the test starts
            if wanted != State.NONE:
                print(f"Starting {SysIdRoutineLog.state_enum_to_string(wanted)}")

        # Decide the voltage for this loop (0 when idle).
        self.volts = self._voltage_for(self.state)

        # Quasistatic ends when the ramp reaches max; dynamic ends after its time window.
        if self.state != State.NONE and self._test_is_over(self.state):
            print(
                f"Finished {SysIdRoutineLog.state_enum_to_string(self.state)}. Release button."
            )
            self.state = State.NONE
            self.finished = True
            self.volts = 0.0

        self._apply_voltage(self.volts)
        self._log_data()

    def end(self) -> None:
        """Robot disabled. Stop the motors and mark the end of testing in the log."""
        self._apply_voltage(0.0)
        self.log.record_state(State.NONE)  # SysId wants a final "none" state in the log
        print("SysId stopped. Load the newest .wpilog in the SysId tool's Analyzer.")

    # ------------------------------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------------------------------

    def _read_buttons(self) -> State:
        """Map gamepad buttons to a test. Face buttons are named by position (south/east/...)."""
        pad = self.robot.controller
        if pad.get_face_down_button():  # A
            return State.QUASISTATIC_FORWARD
        if pad.get_face_right_button():  # B
            return State.QUASISTATIC_REVERSE
        if pad.get_face_left_button():  # X
            return State.DYNAMIC_FORWARD
        if pad.get_face_up_button():  # Y
            return State.DYNAMIC_REVERSE
        return State.NONE

    def _voltage_for(self, state: State) -> float:
        t = self.timer.get()
        if state == State.QUASISTATIC_FORWARD:
            return min(RAMP_VOLTS_PER_SEC * t, MAX_QUASISTATIC_VOLTS)
        if state == State.QUASISTATIC_REVERSE:
            return -min(RAMP_VOLTS_PER_SEC * t, MAX_QUASISTATIC_VOLTS)
        if state == State.DYNAMIC_FORWARD:
            return DYNAMIC_STEP_VOLTS
        if state == State.DYNAMIC_REVERSE:
            return -DYNAMIC_STEP_VOLTS
        return 0.0

    def _test_is_over(self, state: State) -> bool:
        t = self.timer.get()
        if state in (State.QUASISTATIC_FORWARD, State.QUASISTATIC_REVERSE):
            return RAMP_VOLTS_PER_SEC * t >= MAX_QUASISTATIC_VOLTS
        return t >= DYNAMIC_SECONDS

    def _apply_voltage(self, volts: float) -> None:
        """Both sides get the SAME voltage. Right motor inversion is already handled in Robot."""
        throttle = max(-1.0, min(1.0, volts / SUPPLY_VOLTS))
        self.robot.left_motor.set_throttle(throttle)
        self.robot.right_motor.set_throttle(throttle)

    def _log_data(self) -> None:
        """Write one row of data per loop, in the format the SysId tool expects."""
        # Tell the log which test is active (and "none" while idle).
        self.log.record_state(self.state)

        # Per-side measurements. Distances are in meters because of set_distance_per_pulse().
        # (We log the voltage we COMMANDED; that is what the model is fit against.)
        left = self.robot.left_encoder
        right = self.robot.right_encoder
        self.log.motor("drive-left").voltage(self.volts).position(
            left.get_distance()
        ).velocity(left.get_rate())
        self.log.motor("drive-right").voltage(self.volts).position(
            right.get_distance()
        ).velocity(right.get_rate())
