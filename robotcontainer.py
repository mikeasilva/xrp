from commands import *
import constants
from subsystems import *
import wpilib


class RobotContainer:
    def __init__(self):
        self.drive = DriveSubsystem()
        self.led = LED()
        self.joystick = wpilib.XboxController(constants.CONTROLLER_PORT)
        # No joystick, so default command may not be needed.
        # self.drive.setDefaultCommand(...)

    def getAutonomousCommand(self):
        # Drive forward for a bit
        return AutonomousDrive(self.drive, duration=2.0, speed=0.5)
