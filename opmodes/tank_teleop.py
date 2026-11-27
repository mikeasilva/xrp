"""
OPMODE #2: TANK DRIVE TELEOP

Why a second teleop? This shows the payoff of the OpMode framework. Any number of classes can use
@wpilib.teleop, and every one shows up in the Driver Station drop-down. This replaces the old
SendableChooser trick: want a different drive style, a "guest driver" mode, or a slow mode? Just
add another small class. No chooser, no if-statements in a giant teleopPeriodic().

"group" organizes the drop-down. Both drive opmodes share the group "Drive".

Only override the methods you need. Here we skip start(), close() etc. entirely.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import wpilib

if TYPE_CHECKING:
    from robot import Robot


@wpilib.teleop(
    name="Tank Drive",
    group="Drive",
    description="Left stick = left side, right stick = right side",
)
class TankTeleop(wpilib.PeriodicOpMode):
    def __init__(self, robot: Robot) -> None:
        super().__init__()
        self.robot = robot

    def periodic(self) -> None:
        # Each stick directly controls one side. Negated because stick-up reads negative.
        self.robot.drive.tank_drive(
            -self.robot.controller.get_left_y(), -self.robot.controller.get_right_y()
        )

    def end(self) -> None:
        # A driver could disable mid-motion, so stop the motors.
        self.robot.drive.tank_drive(0, 0)
