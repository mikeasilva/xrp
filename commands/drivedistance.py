import commands2


class DriveDistance(commands2.Command):
    def __init__(self, inches: float, drive, network_tables) -> None:
        """Creates a new DriveDistance.
        This command will drive your robot for a desired distance at a desired speed.

        :param inches: The number of inches the robot will drive
        :param drive:  The drive subsystem on which this command will run
        """
        super().__init__()

        self.distance_to_travel = inches
        self.drive = drive
        self.network_tables = network_tables
        self.start_point = None
        self.addRequirements(drive)

    def initialize(self) -> None:
        """Called when the command is initially scheduled."""
        self.drive.stop()
        self.start_point = self.drive.get_location()

    def execute(self) -> None:
        """Called every time the scheduler runs while the command is scheduled."""
        forward_speed = -self.controller.get_left_stick_y() * self.network_tables.read(
            "max-speed"
        )
        self.drive.arcade_drive(forward_speed, 0)

    def end(self, interrupted: bool) -> None:
        """Called once the command ends or is interrupted."""
        self.drive.stop()

    def isFinished(self) -> bool:
        """Returns true when the command should end."""
        # Compare distance travelled from start to desired distance
        current_point = self.drive.get_location()
        return current_point.distance(self.start_point) >= self.distance_to_travel
