import subsystems


class Drivetrain:
    def setup(self):
        self.drivetrain = subsystems.XRPDrivetrain()
        self.imu = subsystems.XRPGyro()

    def execute(self):
        pass
