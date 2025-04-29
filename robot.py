#!/usr/bin/env python3
#
# Run the program
# ---------------
# python -m robotpy sim --xrp
#
# To run the robot tests
# ---------------
# python -m robotpy test

import os

# import random
import constants
from subsystems.arm import Arm
from subsystems.drivetrain import Drivetrain
from subsystems.led import LED

# from subsystems.networktables import NetworkTables
import wpilib
import json

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(wpilib.TimedRobot):
    def robotInit(self) -> None:
        """
        This function is run when the robot is first started up and should be used for any
        initialization code.
        """
        # Assumes a gamepad plugged into channnel 0
        self.joystick = wpilib.Joystick(constants.CONTROLLER_PORT)

        # create a drivetrain (contains two motors, two encoders, a gyro, a distance sensor, and a reflective sensor)
        self.drivetrain = Drivetrain()
        self.arm = Arm()
        self.led = LED()

        # Read in the joystick drift
        try:
            with open("joystick_drift.json", "r") as f:
                self.joystick_drift = json.load(f)
        except:
            self.joystick_drift = {
                "left": 0.0,
                "right": 0.0,
            }

    def robotPeriodic(self) -> None:
        """This function is called periodically (by default, 50 times per second)"""
        super().robotPeriodic()

        # 1. driving: take the speeds from joystick adjusted by the joystick drift
        fwd_speed = (
            -self.joystick.getRawAxis(constants.CONTROLLER_LEFT_STICK)
            + self.joystick_drift["left"]
        )
        turn_speed = (
            self.joystick.getRawAxis(constants.CONTROLLER_RIGHT_STICK)
            + self.joystick_drift["right"]
        )
        distance_to_nearest_object = self.drivetrain.getDistanceToObstacle()
        if (
            distance_to_nearest_object - constants.CRASH_AVOIDANCE_DISTANCE <= 0
            and fwd_speed > 0
        ):
            # Activate crash avoidance mode
            self.drivetrain.stop()
        else:
            self.drivetrain.arcadeDrive(fwd_speed, turn_speed)
            self.drivetrain.periodic()  # updates odometry

        # Read the D-pad value and move the arm accordingly
        dpad = self.joystick.getPOV()
        if dpad != -1:
            shift_by = constants.ARM_SERVO_SHIFT_BY
            if dpad == 0:
                # Up button on D-pad pressed so move the arm up
                self.arm.set_angle(self.arm.get_angle() + shift_by)
            elif dpad == 180:
                # Down button on D-pad pressed so move the arm down
                self.arm.set_angle(self.arm.get_angle() - shift_by)
            elif dpad == 90:
                # Right button on D-pad pressed so turn right on the left wheel
                self.drivetrain.drive_mode = "tank"
                self.drivetrain.drive(-1, 0)
            elif dpad == 270:
                # Left button on D-pad pressed so turn left on the right wheel
                self.drivetrain.drive_mode = "tank"
                self.drivetrain.drive(0, -1)
            self.drivetrain.drive_mode = "arcade"

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
