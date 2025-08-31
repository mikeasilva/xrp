import constants
import subsystems


class Drivetrain:
    def setup(self):
        self.drive = subsystems.XRPDrivetrain()
        self.imu = subsystems.XRPGyro()
        self.mode = "arcade"  # or "tank"
        self.max_output = constants.DEFAULT_MAX_OUTPUT

    def execute(self):
        pass

    def go(self, forward: float, rotation: float):
        self.drive.arcadeDrive(forward * self.max_output, rotation * self.max_output)

    def stop(self):
        self.drive.stop()

    def set_max_output(self, max_output) -> None:
        self.max_output = max_output
