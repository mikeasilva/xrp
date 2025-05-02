import commands2
import os
from robotcontainer import RobotContainer

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(commands2.TimedCommandRobot):
    def robotInit(self):
        self.container = RobotContainer()

    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()

    def autonomousInit(self):
        self.container.led.on()
        command = self.container.getAutonomousCommand()
        if command:
            command.schedule()

    def disabledInit(self) -> None:
        """This function is called once each time the robot enters Disabled mode."""
        self.container.drive.stop()
        self.container.led.off()

    def disabledPeriodic(self) -> None:
        """This function is called periodically when disabled"""
        pass

    def teleopInit(self) -> None:
        """This function is initially when operator control mode runs"""
        pass

    def teleopPeriodic(self) -> None:
        """This function is called periodically when in operator control mode"""
        self.container.led.blink()

    def testInit(self) -> None:
        """This function is called once each time the robot enters test mode."""
        self.container.led.off()
        self.container.drive.stop()
