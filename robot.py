import components
import constants
from magicbot import MagicRobot, feedback
import os
from xrp import XRPMotor
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(MagicRobot):
    controller: components.XboxController
    led: components.XRPLed
    tankdrive: components.TankDrive

    def createObjects(self):
        self.tankdrive_motors = {
            "left_motor": XRPMotor(constants.Ids.LEFT_MOTOR),
            "right_motor": XRPMotor(constants.Ids.RIGHT_MOTOR),
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
        self.controller.capture_button_presses = True

    def teleopPeriodic(self):
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()
        self.tankdrive.drive(-left_y, -right_x)

    @feedback(key="is")
    def getcurrent_state(self):
        """Return the current state of the robot"""
        return self.current_state

    @feedback
    def led_mode(self) -> str:
        return self.led.mode
