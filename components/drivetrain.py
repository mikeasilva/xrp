import components
import magicbot
import wpilib
import wpilib.drive
import wpimath.controller
import xrp


class DriveTrain:
    accelerometer: components.Accelerometer
    gyro: components.Gyro
    left_motor: xrp.XRPMotor
    left_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder

    def execute(self):
        pass

    def setup(self):
        self.right_motor.setInverted(True)
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.distance_PID = wpimath.controller.PIDController(0.1, 0.0, 0.0)
        self.heading_PID = wpimath.controller.PIDController(0.1, 0.0, 0.0)
        self.heading_PID.enableContinuousInput(-180.0, 180.0)
        self.distance_setpoint = 0.0
        self.heading_setpoint = 0.0

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def reset_encoders(self):
        self.left_encoder.reset()
        self.right_encoder.reset()

    def stop(self):
        self.drive.stopMotor()

    def straight(self, distance: float):  # , unit: str = "cm", effort: float = 0.5):
        # Set PID setpoints
        self.distance_setpoint = self.get_distance() + distance
        self.distance_PID.setSetpoint(self.distance_setpoint)
        self.heading_setpoint = self.gyro.yaw()
        self.heading_PID.setSetpoint(self.heading_setpoint)
        # Check if the PID controllers are at their setpoints
        while not self.distance_PID.atSetpoint() and not self.heading_PID.atSetpoint():
            # Get current states
            current_distance = self.get_distance()
            current_heading = self.gyro.yaw()
            # Calculate outputs
            distance_output = self.distance_PID.calculate(
                current_distance, self.distance_setpoint
            )
            heading_output = self.heading_PID.calculate(
                current_heading, self.heading_setpoint
            )
            # Combine the outputs to drive straight
            left_output = distance_output + heading_output
            right_output = distance_output - heading_output
            self.drive.tankDrive(left_output, right_output)

    def turn(self, degree, clockwise: bool = True, effort: float = 0.5):
        # Set the PID setpoint
        current_heading = self.gyro.yaw()
        if clockwise:
            self.heading_setpoint = current_heading + degree
        else:
            self.heading_setpoint = current_heading - degree
        self.heading_PID.setSetpoint(self.heading_setpoint)
        # Check if the PID is at setpoint
        while not self.heading_PID.atSetpoint():
            # Not at setpoint so continue turning
            output = self.heading_PID.calculate(self.gyro.yaw(), self.heading_setpoint)
            self.drive.tankDrive(output, -output)

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Distance")
    def get_distance(self) -> float:
        return (self.get_left_encoder() + self.get_right_encoder()) / 2.0

    @magicbot.feedback(key="Distance Setpoint")
    def get_distance_setpoint(self) -> float:
        return self.distance_setpoint

    @magicbot.feedback(key="Heading Setpoint")
    def get_heading_setpoint(self) -> float:
        return self.heading_setpoint

    @magicbot.feedback(key="Left Encoder")
    def get_left_encoder(self) -> float:
        return self.left_encoder.getDistance()

    @magicbot.feedback(key="Right Encoder")
    def get_right_encoder(self) -> float:
        return self.right_encoder.getDistance()
