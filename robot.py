#!/usr/bin/env python3
"""
THE ROBOT CLASS (RobotPy 2027 alpha, XRP)

In an OpMode project, Robot extends wpilib.OpModeRobot instead of TimedRobot. The big idea:

* Robot  = things that exist for the WHOLE time the program runs (motors, sensors,
           controllers). It is constructed exactly once at startup.
* OpModes = the "programs" the driver picks from a drop-down on the Driver Station. Each one is
           its own class, and a brand-new instance is created every time one is selected.

There is no autonomousInit()/teleopPeriodic() here anymore. That per-mode code now lives in the
classes inside the "opmodes" folder.

HOW OPMODES GET FOUND: classes decorated with @wpilib.teleop / @wpilib.autonomous /
@wpilib.utility are discovered automatically at startup, so there is no registration code here.
(See the commented-out fallback in __init__ if discovery doesn't work on your alpha version.)
"""

import wpilib
import xrp  # separate package from robotpy-xrp (not part of wpilib): pip install robotpy-xrp


class Robot(wpilib.OpModeRobot):
    def __init__(self) -> None:
        # Always call the parent constructor first. This is also where decorated opmodes are
        # discovered and published to the Driver Station.
        super().__init__()

        # -------------------------------------------------------------------------------------
        # FALLBACK: explicit registration. If your RobotPy alpha doesn't auto-discover, replace
        # the super().__init__() line above with the block below. (Names are from the RobotPy
        # discovery pull request and may differ slightly in your version.)
        #
        #   super().__init__(auto_discover=False)
        #   from opmodes.arcade_teleop import ArcadeTeleop
        #   self.add_opmode(ArcadeTeleop, wpilib.RobotMode.TELEOPERATED, "Arcade Drive", "Drive")
        #   self.publish_opmodes()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Shared hardware. Opmodes borrow these through the Robot instance handed to their
        # constructors. Think of Robot as a "toolbox" every opmode reaches into.
        # -------------------------------------------------------------------------------------

        # The XRP needs XRPMotor, NOT the normal PWM motor classes.
        # Motor channel 0 = left motor, channel 1 = right motor.
        self.left_motor = xrp.XRPMotor(0)
        self.right_motor = xrp.XRPMotor(1)

        # One side of a drivetrain must be flipped so +1 means "forward" on both sides.
        # (If your XRP drives backwards or spins in place, flip this to the other motor.)
        self.right_motor.set_inverted(True)

        # DifferentialDrive turns "forward speed + turn rate" into left/right motor outputs.
        # In RobotPy 2027 it lives directly in the wpilib module (there is no wpilib.drive) and
        # takes the motor objects themselves.
        self.drive = wpilib.DifferentialDrive(self.left_motor, self.right_motor)

        # The 2027 Gamepad class (replaces XboxController/PS4Controller). USB port 0.
        self.controller = wpilib.Gamepad(0)

    # ------------------------------------------------------------------------------------------
    # Methods below run NO MATTER WHICH opmode is selected. All are optional overrides.
    # ------------------------------------------------------------------------------------------

    def driver_station_connected(self) -> None:
        """Called once, the first time the Driver Station connects."""
        print("Driver Station connected!")

    def robot_periodic(self) -> None:
        """Called every loop (20 ms) regardless of enabled state or selected opmode."""

    def none_periodic(self) -> None:
        """Called every loop while NO opmode is selected (including when the DS is disconnected)."""


if __name__ == "__main__":
    wpilib.run(Robot)