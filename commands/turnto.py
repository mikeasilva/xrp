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

        self.total_degrees_to_turn = 0.0
        self.drive = drive
        self.target_heading = heading
        self.addRequirements(drive)
        self.max_turn_speed = networktables.read("max-speed")

    def initialize(self) -> None:
        """Called when the command is initially scheduled."""
        self.drive.stop()
        self.total_degrees_to_turn = d = self.get_degrees_to_turn()
        print(f"Need to turn {d} degrees")

    def execute(self) -> None:
        """Called every time the scheduler runs while the command is scheduled."""
        # if self.direction == "CW":
        #    turn_speed = -turn_speed
        self.drive.arcade_drive(0, self.get_turn_speed())
        time.sleep(0.1)

    def end(self, interrupted: bool) -> None:
        """Called once the command ends or is interrupted."""
        self.drive.stop()

    def get_degrees_to_turn(self) -> int:
        """Returns the number of degrees to turn"""
        current_heading = self.drive.get_gyro_angle()
        return round(current_heading - self.target_heading, 0)

    def get_turn_speed(self) -> float:
        """Adjusts the turn speed by the closeness to meeting the turn."""
        degrees_to_turn = self.get_degrees_to_turn()
        p_degrees_to_turn = degrees_to_turn / self.total_degrees_to_turn
        return self.max_turn_speed * p_degrees_to_turn

    def isFinished(self) -> bool:
        """Returns true when the command should end."""
        # Compare distance travelled from start to desired distance
        degrees_to_turn = self.get_degrees_to_turn()
        t = self.get_turn_speed()
        print(degrees_to_turn, t)
        return degrees_to_turn == 0
