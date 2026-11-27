"""
OPMODE #4: UTILITY / DIAGNOSTICS

"Utility" is the renamed Test mode. It's for anything that isn't a match: testing one motor,
checking a sensor, calibrating. Because it's its own opmode, none of this touches your match code.

This one pulses the left motor, then the right, so you can verify wiring and inversion. It also
demonstrates add_periodic(), which runs an extra callback at its OWN rate, separate from the main
20 ms loop.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import wpilib

if TYPE_CHECKING:
    from robot import Robot


@wpilib.utility(
    name="Motor Test", description="Spins left then right motor to check wiring"
)
class MotorTest(wpilib.PeriodicOpMode):
    def __init__(self, robot: Robot) -> None:
        super().__init__()
        self.robot = robot
        self.timer = wpilib.Timer()

        # Register an extra callback: run report() every 0.5 s, offset 10 ms from the main loop
        # so they don't fire at the exact same instant.
        #
        # Callbacks are registered right here at construction and they run EVEN WHILE DISABLED.
        self.add_periodic(self.report, 0.5, 0.01)

    def start(self) -> None:
        self.timer.restart()

    def periodic(self) -> None:
        # Alternate every 2 seconds: left motor, right motor, left, right...
        left_turn = int(self.timer.get() / 2.0) % 2 == 0

        # Drive each motor directly (bypassing DifferentialDrive) to test them individually.
        self.robot.left_motor.set_throttle(0.3 if left_turn else 0.0)
        self.robot.right_motor.set_throttle(0.0 if left_turn else 0.3)

    def end(self) -> None:
        self.robot.left_motor.set_throttle(0)
        self.robot.right_motor.set_throttle(0)

    def report(self) -> None:
        """Our extra 0.5 s callback. Printing is harmless while disabled.

        WARNING: callbacks added with add_periodic() run whether or not the robot is enabled.
        If one of them commands a motor, guard it with an is-enabled check or it will fail while
        disabled. This one only prints, so no guard is needed.
        """
        print(f"Motor Test alive, timer = {self.timer.get():.1f}")
