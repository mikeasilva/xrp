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

import os

import wpilib
import xrp

import constants

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


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
        #
        # import opmodes
        #
        # self.add_opmode(
        #    opmodes.ArcadeTeleop, RobotMode.TELEOPERATED, "Arcade Drive", "Drive"
        # )
        # self.add_opmode(
        #    opmodes.DriveAndTurnAuto, RobotMode.AUTONOMOUS, "Drive and Turn", "Auto"
        # )
        # self.add_opmode(
        #    opmodes.MotorTest, RobotMode.UTILITY, "Motor Test", "Utility"
        # )
        # self.publish_opmodes()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Shared hardware. Opmodes borrow these through the Robot instance handed to their
        # constructors. Think of Robot as a "toolbox" every opmode reaches into.
        # -------------------------------------------------------------------------------------

        # Setup the XRP motors
        self.left_motor = xrp.XRPMotor(constants.Ids.LEFT_MOTOR)
        self.left_motor.set_inverted(constants.LEFT_INVERTED)
        self.right_motor = xrp.XRPMotor(constants.Ids.RIGHT_MOTOR)
        self.right_motor.set_inverted(constants.RIGHT_INVERTED)

        # Setup the drivetrain
        self.drive = wpilib.DifferentialDrive(self.left_motor, self.right_motor)

        # Setup the encoders
        self.left_encoder = wpilib.Encoder(*constants.Ids.LEFT_ENCODER)
        # self.left_encoder.set_reverse_direction(constants.LEFT_INVERTED)
        self.left_encoder.set_distance_per_pulse(constants.DISTANCE_PER_PULSE)
        self.right_encoder = wpilib.Encoder(*constants.Ids.RIGHT_ENCODER)
        # self.right_encoder.set_reverse_direction(constants.RIGHT_INVERTED)
        self.right_encoder.set_distance_per_pulse(constants.DISTANCE_PER_PULSE)

        # Setup the servo
        self.servo = xrp.XRPServo(constants.Ids.SERVO)

        # Setup the sensors
        self.rangefinder = xrp.XRPRangefinder()
        self.reflectance_sensor = xrp.XRPReflectanceSensor()
        self.gyro = xrp.XRPGyro()

        # Setup the on-board LED
        self.led = xrp.XRPOnBoardIO()
        self.led.set_led(False)  # Turn off the LED at startup

        # Setup the controller. The Gamepad class is a new, unified controller class that
        # replaces the XboxController and PS4Controller classes. It supports any USB gamepad,
        # including Xbox, PS4, and generic controllers. The Gamepad class is part of the 2027
        # RobotPy alpha release.
        self.controller = wpilib.Gamepad(constants.Ids.GAMEPAD)

    # ------------------------------------------------------------------------------------------
    # Methods below run NO MATTER WHICH opmode is selected. All are optional overrides.
    # ------------------------------------------------------------------------------------------

    def driver_station_connected(self) -> None:
        """Called once, the first time the Driver Station connects."""
        print("Driver Station connected!")
        self.led.set_led(True)  # Turn on the LED when the DS connects

    def robot_periodic(self) -> None:
        """Called every loop (20 ms) regardless of enabled state or selected opmode."""

    def none_periodic(self) -> None:
        """Called every loop while NO opmode is selected (including when the DS is disconnected)."""
        self.led.set_led(False)  # Turn off the LED when no opmode is selected


if __name__ == "__main__":
    wpilib.run(Robot)
