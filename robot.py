import components
import constants
from magicbot import MagicRobot, feedback
import os
import xrp
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(MagicRobot):
    led: components.LED
    tankdrive: components.TankDrive

    def createObjects(self):
        """Create motors and stuff here"""
        self.tankdrive_motors = {
            "left": xrp.XRPMotor(constants.Channel.LEFT_MOTOR),
            "right": xrp.XRPMotor(constants.Channel.RIGHT_MOTOR),
        }
        self.tankdrive_encoders = {
            "left": wpilib.Encoder(*constants.Channel.LEFT_ENCODER),
            "right": wpilib.Encoder(*constants.Channel.RIGHT_ENCODER),
        }
        self.led_blink_time = constants.LED_BLINK_TIME
        self.current_state = "CREATING OBJECTS"

    def disabledInit(self):
        self.current_state = "DISABLED"

    def disabledPeriodic(self):
        self.led.mode = "off"

    def teleopInit(self):
        """Called when teleop starts; optional"""
        self.led.mode = "blink"

    def teleopPeriodic(self):
        pass

    @feedback(key="is")
    def getcurrent_state(self):
        """Return the current state of the robot"""
        return self.current_state
