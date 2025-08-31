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
import components
import genie
import os

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(genie.GenieRobot):
    arm: components.Arm
    controller: components.XboxController
    controller_port: int
    distance_sensor: components.DistanceSensor
    drivetrain: components.Drivetrain
    led: components.LED
    line_sensor: components.LineSensor

    def createObjects(self):
        self.controller_port = constants.CONTROLLER_PORT

    def teleopPeriodic(self):
        # Blink to indicate telop mode
        self.led.blink(duration=0.1)

    def disabledPeriodic(self):
        pass
