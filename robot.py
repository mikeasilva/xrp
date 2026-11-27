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
import xrp


class Robot(wpilib.OpModeRobot):
    def __init__(self) -> None:
        # Always call the parent constructor first. This is also where decorated opmodes are
        # discovered and published to the Driver Station.
        super().__init__()

        # -------------------------------------------------------------------------------------
        # FALLBACK: explicit registration. If your RobotPy alpha doesn't auto-discover, register
        # the opmodes explicitly using RobotMode from hal.
        #
        # super().__init__(auto_discover=False)
        # from hal import RobotMode
        # from opmodes.arcade_teleop import ArcadeTeleop
        # from opmodes.drive_and_turn_auto import DriveAndTurnAuto
        # from opmodes.motor_test import MotorTest
        # self.add_opmode(ArcadeTeleop, RobotMode.TELEOPERATED, "Arcade Drive", "Drive")
        # self.add_opmode(DriveAndTurnAuto, RobotMode.AUTONOMOUS, "Drive and Turn", "Auto")
        # self.add_opmode(MotorTest, RobotMode.UTILITY, "Motor Test", "Utility")
        # self.publish_opmodes()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Shared hardware. Opmodes borrow these through the Robot instance handed to their
        # constructors. Think of Robot as a "toolbox" every opmode reaches into.
        # -------------------------------------------------------------------------------------

        # Setup the XRP motors
        self.left_motor = xrp.XRPMotor(0)
        self.right_motor = xrp.XRPMotor(1)
        self.right_motor.set_inverted(True)

        # Setup the drivetrain
        self.drive = wpilib.DifferentialDrive(self.left_motor, self.right_motor)

        # Setup the controller. The Gamepad class is a new, unified controller class that 
        # replaces the XboxController and PS4Controller classes. It supports any USB gamepad, 
        # including Xbox, PS4, and generic controllers. The Gamepad class is part of the 2027 
        # RobotPy alpha release. We assume it's connected to USB port 0.
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
