import commands2
import constants


class TeleopDrive(commands2.Command):
    def __init__(self, drive, controller, network_tables):
        super().__init__()
        self.drive = drive
        self.controller = controller
        self.network_tables = network_tables
        self.addRequirements(drive)

    def initialize(self):
        pass

    def execute(self):
        forward_speed = -self.controller.get_left_stick_y() * self.network_tables.read(
            "max-speed"
        )
        turn_speed = -self.controller.get_right_stick_x() * self.network_tables.read(
            "max-speed"
        )
        self.drive.arcade_drive(forward_speed, turn_speed)
        self.drive.periodic()  # updates odometry
        self.network_tables.update(
            "closest-object", self.drive.get_distance_to_obstacle()
        )

    def isFinished(self):
        return False

    def end(self, interrupted):
        self.drive.stop()
