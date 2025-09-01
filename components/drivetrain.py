import constants
from magicbot import feedback
import subsystems


class Drivetrain:
    DISTANCE_TIME_SERIES = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def setup(self):
        self.drivetrain = subsystems.XRPDrivetrain()
        self.imu = subsystems.XRPGyro()
        self.mode = "arcade"  # or "tank"
        self.max_output = constants.DEFAULT_MAX_OUTPUT
        self.drivetrain.set_drive_mode(self.mode)

    def execute(self):
        # Get the current speed of the robot
        distance = self.drivetrain.get_distance_traveled()
        self.drivetrain.reset_encoders()
        # Update the time series
        self.DISTANCE_TIME_SERIES.pop(0)
        self.DISTANCE_TIME_SERIES.append(distance)
        #pass

    @feedback(key="Average Speed")
    def get_average_speed(self) -> float:
        """
        Get the average speed of the robot in inches per second.
        :return: The average speed in inches per second.
        """
        # Return the average of the time series
        return sum(self.DISTANCE_TIME_SERIES) / len(self.DISTANCE_TIME_SERIES)
    
    def go(self, forward: float, rotation: float) -> None:
        """
        Move the robot using arcade drive.
        :param forward: The forward/backward speed (-1 to 1).
        :param rotation: The rotation speed (-1 to 1).
        """
        self.drivetrain.drive(forward * self.max_output, rotation * self.max_output)

    def set_max_output(self, max_output) -> None:
        """
        Set the maximum output for the drivetrain motors.
        :param max_output: The maximum output value (0 to 1).
        """
        if max_output < 0 or max_output > 1:
            raise ValueError("Max output must be between 0 and 1")
        self.max_output = max_output

    def stop(self) -> None:
        """
        Stop the robot.
        """
        self.drivetrain.stop()    
