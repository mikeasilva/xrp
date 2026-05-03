# XRP MagicBot
# To Run: robotpy sim --xrp

from components import (
    XboxController,
    XRPGyro,
    XRPLed,
    XRPTankDrive,
    XRPServo,
    XRPRangefinder,
    XRPReflectanceSensor,
)
from components.odometry import Odometery
import constants
import magicbot
import math
import os
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    # Magicbot components
    controller: XboxController
    gyro: XRPGyro
    led: XRPLed
    servo: XRPServo
    tankdrive: XRPTankDrive
    rangefinder: XRPRangefinder
    reflectance_sensor: XRPReflectanceSensor
    odometry: Odometery
    # Robot specific variables
    name: str = constants.Robot.NAME
    servo_change: float = constants.Robot.SERVO_CHANGE
    ## Cruise control variables set in this class
    cruise_control_enabled: bool = False
    cruise_control_speed: float = 0.0

    def createObjects(self):
        if constants.LOGGING_ENABLED:
            wpilib.DataLogManager.start()
            self.log = wpilib.DataLogManager.getLog()

        self.current_state = "CREATING OBJECTS"

        self.controller_port = constants.Ids.CONTROLLER

        self.gyro_noise_threshold = constants.Robot.GYRO_NOISE_THRESHOLD

        self.servo_channel = constants.Ids.SERVO

        # Distance per pulse is pi * wheel diameter / pulses per revolution * gear ratio
        self.tankdrive_distance_per_pulse = (
            math.pi
            * constants.Robot.WHEEL_DIAMETER_M
            / (constants.Robot.PULSES_PER_REVOLUTION * constants.Robot.GEAR_RATIO)
        )

        self.led_blink_time = constants.LED_BLINK_TIME

    def autonomousInit(self):
        self.current_state = "AUTO INIT"
        self.led.mode = "on"

    def disabledInit(self):
        self.current_state = "DISABLED INIT"

    def disabledPeriodic(self):
        self.current_state = "DISABLED"
        self.led.mode = "off"
        self.tankdrive.stop()

    def teleopInit(self):
        self.current_state = "TELEOP INIT"
        self.led.mode = "blink"

    def teleopPeriodic(self):
        # Cruise Control Check
        if self.cruise_control_enabled:
            self.current_state = "CRUISE CONTROL ENABLED"
            speed = self.cruise_control_speed
        else:
            self.current_state = "HUMAN CONTROLLED"
            speed = -self.controller.left_y

        # Crash Avoidance: Stop the robot if an object is too close
        if self.rangefinder.distance <= constants.Robot.CRASH_AVOIDANCE_THRESHOLD:
            self.current_state = "CRASH AVOIDANCE"
            speed = 0.0

        self.tankdrive.drive(speed, -self.controller.right_x)

        # Servo control with bumpers
        ## Left bumper raises the servo, right bumper lowers it
        if self.controller.left_bumper_pressed():
            self.servo.position += self.servo_change
        elif self.controller.right_bumper_pressed():
            self.servo.position -= self.servo_change

        # Enable/disable cruise control with the Y button
        if self.controller.y_button_was_pressed():
            # Toggle cruise control
            self.cruise_control_enabled = not self.cruise_control_enabled
            # Set the cruise control speed if it's enabled
            if self.cruise_control_enabled:
                self.cruise_control_speed = speed

    @magicbot.feedback(key="name")
    def get_name(self) -> str:
        return self.name

    @magicbot.feedback(key="is")
    def get_current_state(self):
        """Return the current state of the robot"""
        return self.current_state

    @magicbot.feedback
    def pose(self):
        return [
            self.odometry.get_pose_x(),
            self.odometry.get_pose_y(),
            self.gyro.angle,
        ]
