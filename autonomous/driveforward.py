import components
from magicbot import timed_state, state
import magicbot


class DriveForward(magicbot.AutonomousStateMachine):
    # Injected from the definition in robot.py
    drivetrain: components.DriveTrain

    MODE_NAME = "Drive Forward"
    DEFAULT = True
    # Tank drive stabilization using heading
    # Inspiration taken from
    # https://docs.wpilib.org/en/stable/docs/software/hardware-apis/sensors/gyros-software.html
    # The gain for a simple P loop
    P = 1

    @state(first=True, must_finish=True)
    def create_setpoint(self):
        # Set setpoint to current heading at start of auto
        self.heading = self.drivetrain.gyro.getAngle()
        self.next_state("drive_forward")

    @timed_state(duration=3, next_state="finish")
    def drive_forward(self):
        error = self.heading - self.drivetrain.gyro.getAngle()
        # Drives forward continuously at half speed, using the gyro to stabilize the heading
        self.drivetrain.drive.tankDrive(0.5 + self.P * error, 0.5 - self.P * error)

    @state()
    def finish(self):
        self.drivetrain.stop()
