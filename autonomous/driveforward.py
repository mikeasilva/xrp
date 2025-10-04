import components
import magicbot
import wpimath.controller


class DriveForward(magicbot.AutonomousStateMachine):
    # Injected from the definition in robot.py
    drivetrain: components.DriveTrain

    MODE_NAME = "Drive Forward"
    DEFAULT = True
    # Tank drive stabilization using heading
    # Inspiration taken from
    # https://docs.wpilib.org/en/stable/docs/software/hardware-apis/sensors/gyros-software.html
    # The gain for a simple P loop
    P = 0.01
    I = 0.00
    D = 0.001

    @magicbot.state(first=True, must_finish=True)
    def create_setpoint(self):
        # Set setpoint to current heading at start of auto
        self.heading = self.drivetrain.gyro_angle()
        self.pid_controller = wpimath.controller.PIDController(self.P, self.I, self.D)
        self.pid_controller.setSetpoint(0)
        self.next_state("drive_forward")

    @magicbot.timed_state(duration=3, next_state="finish")
    def drive_forward(self):
        error = self.heading - self.drivetrain.gyro_angle()
        adjustment = self.pid_controller.calculate(error)
        self.drivetrain.drive.tankDrive(0.8 + adjustment, 0.8 - adjustment)

    @magicbot.state()
    def finish(self):
        self.drivetrain.stop()
        self.done()
