# from commands import *
import commands
import constants

# from subsystems import *
import subsystems
import wpilib


class RobotContainer:
    def __init__(self):
        self.drive = subsystems.Drive()
        self.led = subsystems.LED()
        self.joystick = wpilib.XboxController(constants.CONTROLLER_PORT)
        self.network_tables = subsystems.NetworkTables()
        # No joystick, so default command may not be needed.
        # self.drive.setDefaultCommand(...)

    def getAutonomousCommand(self):
        # Drive forward for a bit
        return commands.AutonomousDrive(self.drive, duration=2.0, speed=0.5)
