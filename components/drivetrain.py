import magicbot
import ntcore
import wpilib.drive
import xrp


class Drivetrain:
    left_motor: xrp.XRPMotor
    right_motor: xrp.XRPMotor
    network_table_client: ntcore.NetworkTableInstance
    speed = magicbot.tunable(0.0)
    target_heading = magicbot.tunable(0.0)

    def setup(self):
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)

    def go(self, speed: float, rotation: float):
        self.speed = speed
        self.drive.arcadeDrive(speed, rotation, squareInputs=True)

    def stop(self):
        self.speed = 0.0
        # table = self.network_table_client.getTable("robot")
        # table.getEntry("is_moving").setBoolean(False)
        self.drive.stopMotor()

    def execute(self):
        '''
        table = self.network_table_client.getTable("odometry")
        heading = table.getDoubleTopic("heading").subscribe()
        print(f"Current heading: {heading.get()} degrees")
        self.target_heading = heading.get()
        '''
        pass

    def get_speeds(self):
        return self.left_motor.get(), self.right_motor.get()

    def turn_to(self, heading: float, tolerance: float = 0.1) -> None:
        """
        Turn the robot to a specific heading.

        :param heading: The target heading in degrees.
        :param tolerance: The acceptable error in degrees.
        """
        # This method would implement the logic to turn the robot to the specified angle.
        # For now, it is a placeholder.
        pass
