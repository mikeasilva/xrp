import components
import constants
import magicbot
import math
import wpilib
import wpilib.drive
import wpimath.geometry
import wpimath.controller
import wpimath.kinematics
import xrp


class DriveTrain:
    accelerometer: components.Accelerometer
    distance_pid_p: float
    distance_pid_i: float
    distance_pid_d: float
    encoder_units: str
    gyro: components.Gyro
    heading_pid_p: float
    heading_pid_i: float
    heading_pid_d: float
    left_motor: xrp.XRPMotor
    left_encoder: wpilib.Encoder
    right_motor: xrp.XRPMotor
    right_encoder: wpilib.Encoder

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        self.distance_setpoint = 0.0
        self.heading_setpoint = 0.0
        self.set_encoder_units(self.encoder_units)
        self.right_motor.setInverted(True)
        self.drive = wpilib.drive.DifferentialDrive(self.left_motor, self.right_motor)
        self.distance_PID = wpimath.controller.PIDController(
            self.distance_pid_p,
            self.distance_pid_i,
            self.distance_pid_d,
        )
        self.heading_PID = wpimath.controller.PIDController(
            self.heading_pid_p,
            self.heading_pid_i,
            self.heading_pid_d,
        )
        self.heading_PID.enableContinuousInput(-180.0, 180.0)
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d.fromDegrees(self.gyro.yaw()),
            self.left_encoder_distance(),
            self.right_encoder_distance(),
            wpimath.geometry.Pose2d(),
        )

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def reset_encoders(self) -> None:
        self.left_encoder.reset()
        self.right_encoder.reset()

    def reset_gyro(self) -> None:
        self.gyro.reset()

    def reset_odometry(self, pose: wpimath.geometry.Pose2d) -> None:
        self.reset_encoders()
        self.reset_gyro()
        self.odometry.resetPosition(
            wpimath.geometry.Rotation2d.fromDegrees(self.gyro.yaw()),
            self.left_encoder_distance(),
            self.right_encoder_distance(),
            pose,
        )

    def set_encoder_units(self, unit: str) -> None:
        self.encoder_units = unit
        distance_per_pulse = (
            math.pi * constants.WHEEL_DIAMETER[unit]
        ) / constants.COUNTS_PER_REVOLUTION
        self.left_encoder.setDistancePerPulse(distance_per_pulse)
        self.right_encoder.setDistancePerPulse(distance_per_pulse)

    def stop(self) -> None:
        self.drive.stopMotor()

    def straight(self, distance: float, unit: str = "inches") -> None:
        # Set the encoder units
        self.set_encoder_units(unit)
        # Set PID setpoints
        self.distance_setpoint = self.distance() + distance
        self.distance_PID.setSetpoint(self.distance_setpoint)
        self.heading_setpoint = self.gyro.yaw()
        self.heading_PID.setSetpoint(self.heading_setpoint)
        # Check if the PID controllers are at their setpoints
        while not self.distance_PID.atSetpoint() and not self.heading_PID.atSetpoint():
            # Get current states
            current_distance = self.distance()
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

    def tank_drive_voltage(self, left_voltage: float, right_voltage: float) -> None:
        self.left_motor.setVoltage(left_voltage)
        self.right_motor.setVoltage(right_voltage)
        self.drive.feed()

    def turn(self, degree, clockwise: bool = True, effort: float = 0.5) -> None:
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

    def wrap_angle(self, angle_in_radians: float) -> float:
        while angle_in_radians > math.pi:
            angle_in_radians -= 2 * math.pi
        while angle_in_radians < -math.pi:
            angle_in_radians += 2 * math.pi
        return angle_in_radians

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Distance")
    def distance(self) -> float:
        return (self.left_encoder_distance() + self.right_encoder_distance()) / 2.0

    @magicbot.feedback(key="Distance Setpoint")
    def the_distance_setpoint(self) -> float:
        return self.distance_setpoint

    @magicbot.feedback(key="Heading Setpoint")
    def the_heading_setpoint(self) -> float:
        return self.heading_setpoint

    @magicbot.feedback(key="Left Encoder Count")
    def left_encoder_count(self) -> int:
        return self.left_encoder.get()

    @magicbot.feedback(key="Left Encoder Distance")
    def left_encoder_distance(self) -> float:
        return self.left_encoder.getDistance()

    @magicbot.feedback(key="Right Encoder Count")
    def right_encoder_count(self) -> int:
        return self.right_encoder.get()

    @magicbot.feedback(key="Right Encoder Distance")
    def right_encoder_distance(self) -> float:
        return self.right_encoder.getDistance()

    # @magicbot.feedback(key="Wheel Speed")
    def wheel_speed(self) -> float:
        return wpimath.kinematics.DifferentialDriveWheelSpeeds(
            self.left_encoder.getRate(), self.right_encoder.getRate()
        )
