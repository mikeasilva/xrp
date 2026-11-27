"""
OPMODE #3: A SIMPLE TIMED AUTONOMOUS

Drives forward for 2 seconds, turns for 1 second, then stops.

THE LESSON HERE: constructor time is not enable time.

__init__ runs when the operator SELECTS this auto, which may be minutes before the match starts.
If we started the timer in __init__, it would already be way past 3 seconds by the time the robot
is enabled and the auto would do nothing. So we create the timer in __init__ but start it in
start(), which fires at the moment of enable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import wpilib

if TYPE_CHECKING:
    from robot import Robot

# Tunable constants, named so the code below reads like a plan.
DRIVE_SECONDS = 2.0
TURN_SECONDS = 1.0
DRIVE_SPEED = 0.5
TURN_SPEED = 0.5


@wpilib.autonomous(
    name="Drive And Turn", group="Basic", description="Forward 2s, turn 1s, stop"
)
class DriveAndTurnAuto(wpilib.PeriodicOpMode):
    def __init__(self, robot: Robot) -> None:
        super().__init__()
        self.robot = robot
        self.timer = wpilib.Timer()  # created, but NOT started

    def start(self) -> None:
        """Called once when the robot is enabled: the autonomous "clock" begins here."""
        self.timer.restart()

    def periodic(self) -> None:
        """Every 20 ms while enabled. Each loop we look at the clock and decide what to do.

        We call arcade_drive() on EVERY pass in every branch, including the "stop" branch.
        DifferentialDrive has motor safety enabled, which stops the motors (and complains) if
        it isn't updated regularly.
        """
        if not self.timer.has_elapsed(DRIVE_SECONDS):
            # Phase 1: straight ahead.
            self.robot.drive.arcade_drive(DRIVE_SPEED, 0)
        elif not self.timer.has_elapsed(DRIVE_SECONDS + TURN_SECONDS):
            # Phase 2: spin in place.
            self.robot.drive.arcade_drive(0, TURN_SPEED)
        else:
            # Phase 3: done. Keep telling the drive "0" so motor safety stays happy.
            self.robot.drive.arcade_drive(0, 0)

    def end(self) -> None:
        """Runs when the robot disables (auto ends or the driver hits disable)."""
        self.robot.drive.arcade_drive(0, 0)
