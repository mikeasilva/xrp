# XRP MagicBot
# To Run: robotpy sim --xrp

import components
import constants
import magicbot
import os
import xrp
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    controller: components.XboxController
    gyro: components.XRPGyro
    led: components.XRPLed
    tankdrive: components.TankDrive

    def createObjects(self):
        self.gyro_noise_threshold = constants.Robot.GYRO_NOISE_THRESHOLD

        self.tankdrive_motors = {
            "left_motor": xrp.XRPMotor(constants.Ids.LEFT_MOTOR),
            "right_motor": xrp.XRPMotor(constants.Ids.RIGHT_MOTOR),
        }

        self.controller_port = constants.Ids.CONTROLLER

        self.tankdrive_encoders = {
            "left_encoder": wpilib.Encoder(*constants.Ids.LEFT_ENCODER),
            "right_encoder": wpilib.Encoder(*constants.Ids.RIGHT_ENCODER),
        }

        self.led_blink_time = constants.LED_BLINK_TIME
        self.current_state = "CREATING OBJECTS"

    def autonomousInit(self):
        self.current_state = "AUTO INIT"
        self.led.mode = "on"

    def disabledInit(self):
        self.current_state = "DISABLED INIT"

    def disabledPeriodic(self):
        self.current_state = "DISABLED"
        self.led.mode = "off"

    def teleopInit(self):
        self.current_state = "TELEOP INIT"
        self.led.mode = "blink"

    def teleopPeriodic(self):
        self.tankdrive.drive(-self.controller.left_y, -self.controller.right_x)

    @magicbot.feedback(key="is")
    def get_current_state(self):
        """Return the current state of the robot"""
        return self.current_state
