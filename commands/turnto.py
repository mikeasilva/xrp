import commands2
import time


class TurnTo(commands2.Command):
    def __init__(self, heading: float, drive, networktables) -> None:
        """This command will turn the robot to a desired heading.

        :param heading: The desired heading in degrees (0-360)
        :param drive:  The drivetrain subsystem on which this command will run
        :param networktables: The network tables subsystem for reading values
        """
        super().__init__()

        self.drive = drive
        self.network_tables = networktables
        self.target_heading = heading
        self.addRequirements(drive)

    def initialize(self) -> None:
        """Called when the command is initially scheduled."""
        self.drive.stop()

    def execute(self) -> None:
        """Called every time the scheduler runs while the command is scheduled."""
        turn_speed = self.network_tables.read("max-speed")
        #if self.direction == "CW":
        #    turn_speed = -turn_speed
        self.drive.arcade_drive(0, 0.6)
        time.sleep(0.1)

    def end(self, interrupted: bool) -> None:
        """Called once the command ends or is interrupted."""
        self.drive.stop()

    def isFinished(self) -> bool:
        """Returns true when the command should end."""
        # Compare distance travelled from start to desired distance
        current_heading = self.drive.get_gyro_angle()
        print(current_heading)
        return round(current_heading - self.target_heading, 0) == 0
