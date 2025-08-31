import subsystems


class Drivetrain:
    def setup(self):
        self.drive = subsystems.XRPDrivetrain()
        self.imu = subsystems.XRPGyro()
        self.mode = "arcade"  # or "tank"

    def execute(self):
        pass

    def go(self, forward: float, rotation: float):
        self.drive.arcadeDrive(forward, rotation)

    def stop(self):
        self.drive.stop()
