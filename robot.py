import commands2
import constants
import os
from robotcontainer import RobotContainer

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(commands2.TimedCommandRobot):
    def robotInit(self):
        self.container = RobotContainer()

    def robotPeriodic(self):
        super().robotPeriodic()
        # TODO: Get the max speed from network tables
        # 1. driving: Adjust the max speed based on the joystick input
        forward_speed = (
            -self.container.joystick.getRawAxis(constants.JOYSTICK_LEFT_Y)
            * 1#self.container.network_tables.get("max-speed")
        )
        turn_speed = (
            -self.container.joystick.getRawAxis(constants.JOYSTICK_RIGHT_X)
            * 1#self.container.network_tables.get("max-speed")
        )
        self.container.drive.arcade_drive(forward_speed, turn_speed)
        self.container.drive.periodic()  # updates odometry

        commands2.CommandScheduler.getInstance().run()

    def autonomousInit(self):
        self.container.led.on()
        self.container.network_tables.state.set("autonomous")
        self.autonomous_command = self.container.getAutonomousCommand()
        if self.autonomous_command:
            self.autonomous_command.schedule()

    def disabledInit(self) -> None:
        """This function is called once each time the robot enters Disabled mode."""
        self.container.network_tables.state.set("disabled")
        self.container.drive.stop()
        self.container.led.off()

    def disabledPeriodic(self) -> None:
        """This function is called periodically when disabled"""
        pass

    def teleopInit(self) -> None:
        """This function is initially when operator control mode runs"""
        self.container.network_tables.state.set("teleop")
        if self.autonomous_command:
            self.autonomous_command.cancel()

    def teleopPeriodic(self) -> None:
        """This function is called periodically when in operator control mode"""
        self.container.led.blink()

    def testInit(self) -> None:
        """This function is called once each time the robot enters test mode."""
        self.container.network_tables.state.set("test")
        self.container.led.off()
        commands2.CommandScheduler.getInstance().cancelAll()
        self.container.drive.stop()
