import commands2
import time


class Turn(commands2.Command):
    def __init__(self, degrees: float, direction: str, drive, networktables) -> None:
        """This command will rotate your robot for a desired angle distance.

        :param degrees: The number of degrees the robot will turn, less than 180
        :param direction: The direction to turn, either "CW" or "CCW"
        :param drive:  The drivetrain subsystem on which this command will run
        :param networktables: The network tables subsystem for reading values
        """
        super().__init__()

        assert degrees > 0, "only positive turning angles are supported"
        assert degrees < 135, "only values under 135 degrees are supported"

        if direction not in ["CW", "CCW"]:
            raise ValueError("Direction must be either 'CW' or 'CCW'")

        self.degrees_to_turn = degrees
        self.direction = direction
        self.drive = drive
        self.network_tables = networktables
        self.start_heading = None
        self.addRequirements(drive)

    def initialize(self) -> None:
        """Called when the command is initially scheduled."""
        self.drive.stop()
        self.start_heading = self.drive.get_gyro_angle()

    def execute(self) -> None:
        """Called every time the scheduler runs while the command is scheduled."""
        turn_speed = self.network_tables.read("max-speed")
        if self.direction == "CW":
            turn_speed = -turn_speed
        self.drive.arcade_drive(0, turn_speed)
        time.sleep(0.1)

    def end(self, interrupted: bool) -> None:
        """Called once the command ends or is interrupted."""
        self.drive.stop()

    def isFinished(self) -> bool:
        """Returns true when the command should end."""
        # Compare distance travelled from start to desired distance
        current_heading = self.drive.get_gyro_angle()
        return abs(current_heading - self.start_heading) >= self.degrees_to_turn
