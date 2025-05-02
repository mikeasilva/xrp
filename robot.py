#!/usr/bin/env python3
#
# Run the program
# ---------------
# python -m robotpy sim --xrp
#
# To run the robot tests
# ---------------
# python -m robotpy test

import commands2
import ntcore
import os
import wpilib
from robotcontainer import RobotContainer

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(wpilib.TimedRobot):
    def robotInit(self) -> None:
        """
        This function is run when the robot is first started up and should be used for any
        initialization code.
        """
        # Set up the network tables
        network_tables = ntcore.NetworkTableInstance.getDefault()
        table = network_tables.getTable("XRP")
        self.mode_pub = table.getStringTopic("mode").publish()
        self.mode_pub.set("Init")
        self.robotContainer = RobotContainer(self)

        # Initialize the robot
        # self.controller = wpilib.XboxController(constants.CONTROLLER_PORT)
        # self.drivetrain = Drivetrain(constants.DRIVE_MODE)

    # Every 20ms in all modes
    def robotPeriodic(self):
        commands2.CommandScheduler.getInstance().run()

    def autonomousInit(self):
        """This autonomous runs the autonomous command selected by your RobotContainer class."""
        self.mode_pub.set("Autonomous")
        # Or, just import AutonomousCommand function? What's point of this indirection?
        self.autonomous_command = self.container.getAutonomousCommand()
        if self.autonomous_command:
            self.autonomous_command.schedule()

    def autonomousPeriodic(self) -> None:
        """This function is called periodically during autonomous"""
        pass

    def disabledInit(self) -> None:
        """This function is called once each time the robot enters Disabled mode."""
        self.mode_pub.set("Disabled")

    def disabledPeriodic(self) -> None:
        """This function is called periodically when disabled"""
        pass

    def teleopInit(self):
        self.mode_pub.set("Teleop")
        # This makes sure that the autonomous stops running when
        # teleop starts running. If you want the autonomous to
        # continue until interrupted by another command, remove
        # this line or comment it out.
        if self.autonomous_command:
            self.autonomous_command.cancel()

    def teleopPeriodic(self) -> None:
        """This function is called periodically during operator control"""
        pass

    def testInit(self):
        self.mode_pub.set("Test")
        # Cancels all running subsystems at the start of test mode
        commands2.CommandScheduler.getInstance().cancelAll()
        self.test_command = self.robotContainer.getTestCommand()
        # schedule the command
        if self.test_command is not None:
            self.test_command.schedule()

    def testPeriodic(self) -> None:
        """This function is called periodically during test mode"""
        pass
