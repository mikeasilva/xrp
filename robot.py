#!/usr/bin/env python3
#
# Run the program
# ---------------
# python -m robotpy sim --xrp
#
# To run the robot tests
# ---------------
# python -m robotpy test

import constants
import ntcore
import os
from subsystems.arm import Arm
from subsystems.drivetrain import Drivetrain
from subsystems.led import LED
from subsystems.joystick import Joystick

# from subsystems.networktables import NetworkTables
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(wpilib.TimedRobot):
    def robotInit(self) -> None:
        """
        This function is run when the robot is first started up and should be used for any
        initialization code.
        """
        # Create the subsytems objects
        self.arm = Arm()
        self.drivetrain = Drivetrain()
        self.joystick = Joystick()
        self.led = LED()
        # self.network_tables = NetworkTables()
        network_tables = ntcore.NetworkTableInstance.getDefault()
        table = network_tables.getTable("XRP")
        self.crash_pub = table.getBooleanTopic("crash-avoidance-activated").publish()

    def robotPeriodic(self) -> None:
        """This function is called periodically (by default, 50 times per second)"""
        super().robotPeriodic()

        # 1. driving: take the speeds from joystick
        forward_speed = -self.joystick.get_left_stick()
        turn_speed = -self.joystick.get_right_stick()
        self.drivetrain.arcade_drive(forward_speed, turn_speed)
        self.drivetrain.periodic()  # updates odometry

        # 2. update network tables
        self.crash_pub.set(self.drivetrain.at_risk_of_crashing(1))

        # Read the D-pad value and move the arm accordingly
        dpad = self.joystick.get_dpad()
        if dpad != -1:
            shift_by = constants.ARM_SERVO_SHIFT_BY
            if dpad == 0:
                # Up button on D-pad pressed so move the arm up
                # self.arm.set_angle(self.arm.get_angle() + shift_by)
                self.arm.retract_arm()
            elif dpad == 180:
                # Down button on D-pad pressed so move the arm down
                # self.arm.set_angle(self.arm.get_angle() - shift_by)
                self.arm.extend_arm()
            elif dpad == 90:
                # Right button on D-pad pressed so turn right on the left wheel
                self.drivetrain.tank_drive(1, 0)
            elif dpad == 270:
                # Left button on D-pad pressed so turn left on the right wheel
                self.drivetrain.tank_drive(0, 1)

    def teleopPeriodic(self) -> None:
        """This function is called periodically when in operator control mode"""
        self.led.blink()

    def teleopInit(self) -> None:
        """This function is initially when operator control mode runs"""
        pass

    def disabledInit(self) -> None:
        """This function is called once each time the robot enters Disabled mode."""
        self.drivetrain.stop()
        self.led.off()

    def disabledPeriodic(self) -> None:
        """This function is called periodically when disabled"""
        pass

    def autonomousInit(self) -> None:
        """This autonomous runs the autonomous command selected by your RobotContainer class."""
        self.drivetrain.stop()
        self.led.on()

    def autonomousPeriodic(self) -> None:
        """This function is called periodically during autonomous"""
        pass

    def testInit(self) -> None:
        """Cancels all running commands at the start of test mode"""
        self.drivetrain.stop()
        self.led.off()
