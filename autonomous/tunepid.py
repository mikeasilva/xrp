import components
import magicbot
import random
import wpimath.controller


class DriveForward(magicbot.AutonomousStateMachine):
    # Injected from the definition in robot.py
    drivetrain: components.DriveTrain

    MODE_NAME = "Tune PID"
    DEFAULT = False
    FILE_NAME = "pid_tuning.csv"
    P = 0.01
    I = 0.0
    D = 0.001

    @magicbot.state(first=True, must_finish=True)
    def start_up(self):
        self.errors = []
        self.n = 0
        self.n_runs = 10
        # create file if it doesn't exist
        try:
            with open(self.FILE_NAME, "x") as f:
                f.write("P,I,D,MSE,N,DISTANCE\n")
        except FileExistsError:
            pass
        self.next_state("create_setpoint")

    @magicbot.state(first=False, must_finish=True)
    def create_setpoint(self):
        # Set setpoint to current heading at start of auto
        self.heading = self.drivetrain.heading_in_degrees()
        self.drivetrain.reset_encoders()
        self.pid_controller = wpimath.controller.PIDController(self.P, self.I, self.D)
        self.pid_controller.setSetpoint(0)
        self.next_state("drive_forward")

    @magicbot.timed_state(duration=3, next_state="drive_backwards")
    def drive_forward(self):
        error = self.heading - self.drivetrain.heading_in_degrees()
        self.errors.append(error)
        adjustment = self.pid_controller.calculate(error)
        self.drivetrain.drive.tankDrive(0.85 + adjustment, 0.85 - adjustment)
        self.distance = self.drivetrain.distance()

    @magicbot.timed_state(duration=3, next_state="save_data")
    def drive_backwards(self):
        self.drivetrain.drive.tankDrive(-0.8, -0.8)

    @magicbot.state()
    def save_data(self):
        squared_errors = [e**2 for e in self.errors]
        mse = sum(squared_errors) / len(squared_errors)
        with open(self.FILE_NAME, "a") as f:
            f.write(
                f"{self.P},{self.I},{self.D},{mse},{len(squared_errors)},{self.distance}\n"
            )
        self.errors = []
        self.n = self.n + 1
        if self.n < self.n_runs:
            self.next_state("randomize_pid")
        else:
            self.next_state("finish")

    @magicbot.state()
    def randomize_pid(self):
        self.P = round(random.uniform(0.001, 0.1), 3)
        self.I = round(random.uniform(0.001, 0.1), 3)
        self.D = round(random.uniform(0.001, 0.1), 3)
        self.next_state("create_setpoint")

    @magicbot.state()
    def finish(self):
        self.drivetrain.stop()

        self.done()
