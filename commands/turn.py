# from __future__ import annotations
import commands2
from subsystems.drivetrain import Drivetrain


class Turn(commands2.Command):
    def __init__(
        self, 
        degrees: float, 
        direction: str = "CW", 
        margin_of_error: float = 0.5,
        drivetrain: Drivetrain = None
    ) -> None:
        """
        Command to turn the robot a specified number of degrees.
        :param degrees: the number of degrees to turn
        :param direction: the direction to turn, either "CW" (clockwise) or "CCW" (counter-clockwise)
        :param margin_of_error: the margin of error of the turn in degrees (default: 0.5)
        """
        super().__init__()
        self.drivetrain = drivetrain
        self.addRequirements(self.drivetrain)

        self.degrees = degrees
        self.direction = direction.upper()
        if self.direction not in ["CW", "CCW"]:
            raise ValueError("Direction must be either 'CW' or 'CCW'")
        self.margin_of_error = margin_of_error
        self.heading_start = self.drivetrain.get_gyro_angle_z()
        # self.left_delta = 0
        # self.right_delta = 0
        # self.left_start = self.drivetrain.get_left_encoder_position()
        # self.right_start = self.drivetrain.get_right_encoder_position()

    def initialize(self):
        pass

    def execute(self):
        """Execute the turn command."""
        if self.direction == "CW":
            self.drivetrain.arcade_drive(0, -0.5)
        else:
            self.drivetrain.arcade_drive(0, 0.5)

    def isFinished(self) -> bool:
        """Check if the robot has turned the specified number of degrees."""
        current_heading = self.drivetrain.get_gyro_angle_z()
        degrees_turned = abs(current_heading - self.heading_start)
        '''
        return abs(degrees_turned + self.margin_of_error) >= abs(self.degrees) or abs(
            degrees_turned - self.margin_of_error
        ) >= abs(self.degrees)
        '''
        return abs(degrees_turned) >= abs(self.degrees)

    def end(self, interrupted: bool):
        self.drivetrain.stop()
