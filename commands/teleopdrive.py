import commands2
import constants
# import wpilib


class TeleopDrive(commands2.Command):
    def __init__(self, drive, joystick, network_tables):
        super().__init__()
        self.drive = drive
        self.joystick = joystick
        self.network_tables = network_tables
        self.addRequirements(drive)

    def initialize(self):
        pass

    def execute(self):
        # self.drive.arcade_drive(1, 0)
        # self.drive.periodic()

        # TODO: Get the max speed from network tables
        max_speed = self.network_tables.read("max-speed")
        # 1. driving: Adjust the max speed based on the joystick input
        forward_speed = (
            -self.joystick.getRawAxis(constants.JOYSTICK_LEFT_Y)
            * self.network_tables.read("max-speed")
        )
        turn_speed = (
            -self.joystick.getRawAxis(constants.JOYSTICK_RIGHT_X)
            * self.network_tables.read("max-speed")
        )
        self.drive.arcade_drive(forward_speed, turn_speed)
        self.drive.periodic()  # updates odometry

    def isFinished(self):
        return False

    def end(self, interrupted):
        self.drive.stop()
