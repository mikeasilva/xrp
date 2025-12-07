import components
import magicbot


class DriveForward(magicbot.AutonomousStateMachine):
    # Injected from the definition in robot.py
    drivetrain: components.DriveTrain

    MODE_NAME = "Drive Forward"
    DEFAULT = True

    @magicbot.state(first=True, must_finish=True)
    def create_setpoint(self):
        # Set setpoint to current heading at start of auto
        self.initial_heading = self.drivetrain.gyro.yaw()
        self.drivetrain.set_heading_pid_setpoint(0)
        self.next_state("drive_forward")

    @magicbot.timed_state(duration=3, next_state="finish")
    def drive_forward(self):
        error = self.initial_heading - self.drivetrain.gyro.yaw()
        adjustment = self.drivetrain.heading_PID.calculate(error)
        self.drivetrain.tank_drive(0.8 + adjustment, 0.8 - adjustment)

    @magicbot.state()
    def finish(self):
        self.drivetrain.stop()
        self.done()
