"""
OPMODE #1: ARCADE DRIVE TELEOP

Anatomy of an opmode:

1. The @wpilib.teleop decorator puts this class in the Driver Station's teleop drop-down.
   (All decorator options are optional; the name defaults to the class name.)
2. It extends wpilib.PeriodicOpMode, which calls our methods on a fixed 20 ms loop.
3. The constructor takes the Robot. WPILib passes it in automatically, so we never create it.

LIFECYCLE (in order):

    operator selects opmode on DS  -> __init__ runs (new instance created)
    robot still disabled           -> disabled_periodic() every 20 ms
    operator presses Enable        -> start() once
    robot enabled                  -> periodic() every 20 ms
    operator presses Disable       -> end() once, then close()
    (a fresh instance is built if an opmode is still selected)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import wpilib

if TYPE_CHECKING:
    # Only imported for type hints/autocomplete. Importing Robot for real here could create a
    # circular import, since the robot is what discovers this file.
    from robot import Robot


@wpilib.teleop(
    name="Arcade Drive",
    group="Drive",
    description="Left stick drives, right stick turns",
)
class ArcadeTeleop(wpilib.PeriodicOpMode):
    def __init__(self, robot: Robot) -> None:
        """Runs when the operator SELECTS this opmode, not when they enable.

        There is no separate init method: do all setup here. Keep it quick and don't assume
        the robot is enabled yet.
        """
        super().__init__()
        self.robot = robot  # our handle to the shared hardware

    def disabled_periodic(self) -> None:
        """Every loop while this opmode is selected but the robot is DISABLED.

        Great for previewing: show sensor values, check the controller is plugged in, etc.
        The library guarantees this runs at least once before the first start().
        (We can't move motors here; the robot is disabled.)
        """

    def start(self) -> None:
        """Exactly ONCE at the moment the robot becomes enabled.

        Use it to reset timers or accumulators. It must return quickly; ongoing work belongs
        in periodic().
        """
        print("Arcade Drive enabled")

    def periodic(self) -> None:
        """Every 20 ms while ENABLED. This is the old teleopPeriodic()."""
        # Joystick "up" reads as a NEGATIVE number, so negate it to make up = forward.
        forward = -self.robot.controller.get_left_y()
        turn = -self.robot.controller.get_right_x()
        self.robot.drive.arcade_drive(forward, turn)

    def end(self) -> None:
        """Once when the robot is DISABLED after having been enabled. Stop things safely."""
        self.robot.drive.arcade_drive(0, 0)

    def close(self) -> None:
        """When this opmode is de-selected. The object is thrown away and never reused.

        Release resources here (files, etc.). We have none.
        """
