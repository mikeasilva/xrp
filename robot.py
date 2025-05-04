import commands2
import os
from robotcontainer import RobotContainer

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(commands2.TimedCommandRobot):
    def robotInit(self):
        self.container = RobotContainer()
        self.autonomous_command = self.container.get_autonomous_command()

    def robotPeriodic(self):
        super().robotPeriodic()
        self.container.network_tables.update(
            "x", self.container.drive.get_gyro_angle_x()
        )
        self.container.network_tables.update(
            "y", self.container.drive.get_gyro_angle_y()
        )
        self.container.network_tables.update("z", self.container.drive.get_gyro_angle())
        commands2.CommandScheduler.getInstance().run()

    def autonomousInit(self):
        self.container.led.on()
        self.container.network_tables.update("state", "autonomous")
        if self.autonomous_command:
            self.autonomous_command.schedule()

    def disabledInit(self) -> None:
        """This function is called once each time the robot enters Disabled mode."""
        self.container.drive.stop()
        self.container.led.off()
        self.container.network_tables.update("state", "disabled")
        commands2.CommandScheduler.getInstance().cancelAll()

    def teleopInit(self) -> None:
        """This function is initially when operator control mode runs"""
        self.container.network_tables.update("state", "teleop")
        if self.autonomous_command:
            self.autonomous_command.cancel()

    def teleopPeriodic(self) -> None:
        """This function is called periodically when in operator control mode"""
        self.container.led.blink()

    def testInit(self) -> None:
        """This function is called once each time the robot enters test mode."""
        self.container.drive.stop()
        self.container.led.off()
        self.container.network_tables.update("state", "test")
        commands2.CommandScheduler.getInstance().cancelAll()
