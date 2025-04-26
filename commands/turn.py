# from __future__ import annotations
import commands2
from subsystems.drivetrain import Drivetrain


class Turn(commands2.Command):
    def __init__(self, turn_degrees: float, speed: float = 0.5, timeout: float = None):
        """
        Command to turn the robot a specified number of degrees.
        :param turn_degrees: the number of degrees to turn (positive for right, negative for left)
        :param speed: the speed of the turn (default is 0.5)
        :param timeout: the time limit for the command (default is None, meaning no timeout)
        """
        super().__init__()
        self.drivetrain = Drivetrain()
        self.addRequirements(self.drivetrain)

        # ensure distance is always positive while speed could be either positive or negative
        if turn_degrees < 0:
            speed *= -1
            turn_degrees *= -1

        self.turn_degrees = turn_degrees
        self.speed = speed
        self.timeout = timeout
        self.left_delta = 0
        self.right_delta = 0
        self.left_start = self.drivetrain.get_left_encoder_position()
        self.right_start = self.drivetrain.get_right_encoder_position()

    def initialize(self):
        pass

    def execute(self):
        pass

    def isFinished(self) -> bool:
        pass

    def end(self, interrupted: bool):
        self.drivetrain.stop()
