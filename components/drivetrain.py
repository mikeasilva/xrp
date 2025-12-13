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
    ACCELEROMETER: components.Accelerometer
    DISTANCE_PID_P: float
    DISTANCE_PID_I: float
    DISTANCE_PID_D: float
    ENCODER_UNITS: str
    GYRO: components.Gyro
    HEADING_PID_P: float
    HEADING_PID_I: float
    HEADING_PID_D: float
    LEFT_MOTOR: xrp.XRPMotor
    LEFT_ENCODER: wpilib.Encoder
    RIGHT_MOTOR: xrp.XRPMotor
    RIGHT_ENCODER: wpilib.Encoder

    DISTANCE_SETPOINT = 0.0
    EFFORT = 0.8
    HEADING_SETPOINT = 0.0

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        self.set_encoder_units(self.ENCODER_UNITS)
        self.drive = wpilib.drive.DifferentialDrive(self.LEFT_MOTOR, self.RIGHT_MOTOR)
        self.distance_pid = wpimath.controller.PIDController(
            self.DISTANCE_PID_P,
            self.DISTANCE_PID_I,
            self.DISTANCE_PID_D,
        )
        self.heading_pid = wpimath.controller.PIDController(
            self.HEADING_PID_P,
            self.HEADING_PID_I,
            self.HEADING_PID_D,
        )
        self.heading_pid.enableContinuousInput(-180.0, 180.0)
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            wpimath.geometry.Rotation2d.fromDegrees(self.GYRO.yaw()),
            self.left_encoder_distance(),
            self.right_encoder_distance(),
            wpimath.geometry.Pose2d(),
        )

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def arcade_drive(self, forward: float, rotation: float) -> None:
        forward *= self.EFFORT
        rotation *= self.EFFORT
        self.drive.arcadeDrive(forward, rotation)

    def reset_encoders(self) -> None:
        self.LEFT_ENCODER.reset()
        self.RIGHT_ENCODER.reset()

    def reset_gyro(self) -> None:
        self.GYRO.reset()

    def reset_odometry(self, pose: wpimath.geometry.Pose2d) -> None:
        self.reset_encoders()
        self.reset_gyro()
        self.odometry.resetPosition(
            wpimath.geometry.Rotation2d.fromDegrees(self.GYRO.yaw()),
            self.left_encoder_distance(),
            self.right_encoder_distance(),
            pose,
        )

    def set_effort(self, effort: float) -> None:
        self.EFFORT = effort

    def set_encoder_units(self, unit: str) -> None:
        self.ENCODER_UNITS = unit
        distance_per_pulse = (
            math.pi * constants.WHEEL_DIAMETER[unit]
        ) / constants.COUNTS_PER_REVOLUTION
        self.LEFT_ENCODER.setDistancePerPulse(distance_per_pulse)
        self.RIGHT_ENCODER.setDistancePerPulse(distance_per_pulse)

    def set_distance_pid_setpoint(self, setpoint: float) -> None:
        self.DISTANCE_SETPOINT = setpoint
        self.distance_pid.setSetpoint(setpoint)

    def set_heading_pid_setpoint(self, setpoint: float) -> None:
        self.HEADING_SETPOINT = setpoint
        self.heading_pid.setSetpoint(setpoint)

    def stop(self) -> None:
        self.drive.stopMotor()

    def tank_drive(self, left_speed: float, right_speed: float) -> None:
        left_speed *= self.EFFORT
        right_speed *= self.EFFORT
        self.drive.tankDrive(left_speed, right_speed)

    def straight(self, distance: float, unit: str = "inches") -> None:
        # Set the encoder units
        self.set_encoder_units(unit)
        # Set PID setpoints
        self.initial_heading = self.GYRO.yaw()
        self.reset_encoders()
        self.set_distance_pid_setpoint(distance)
        self.set_heading_pid_setpoint(self.initial_heading)
        # Check if the PID controllers are at their setpoints
        while True:
            left_delta = self.left_encoder_distance() - distance
            right_delta = self.right_encoder_distance() - distance
            dist_traveled = (left_delta + right_delta) / 2
            distance_error = distance - dist_traveled
            effort = self.distance_pid.calculate(distance_error)
            if self.distance_pid.atSetpoint():
                self.stop()
                break
            adjustment = self.heading_pid.calculate(self.initial_heading - self.GYRO.yaw())
            left_val = self.bounded(effort + adjustment)
            right_val = self.bounded(effort - adjustment)
            self.tank_drive(left_val, right_val)
            print(f"Distance: {self.distance()}  Setpoint: {distance}; Right {right_val}; Left {left_val}")

    def bounded(self, val, max_val=1, min_val=-1):
        return max(min_val, min(val, max_val))
    '''
    def tank_drive_voltage(self, left_voltage: float, right_voltage: float) -> None:
        self.LEFT_MOTOR.setVoltage(left_voltage)
        self.RIGHT_MOTOR.setVoltage(right_voltage)
        self.drive.feed()

    def turn(self, turn_degrees: float, max_effort: float = 0.5, timeout: float = None, main_controller: Controller = None, secondary_controller: Controller = None, use_imu:bool = True) -> bool:
        """
        Turn the robot some relative heading given in turnDegrees, and exit function when the robot has reached that heading.
        effort is bounded from -1 (turn counterclockwise the relative heading at full speed) to 1 (turn clockwise the relative heading at full speed)
        Uses the IMU to determine the heading of the robot and P control for the motor controller.

        :param turnDegrees: The number of angle for the robot to turn (In Degrees)
        :type turnDegrees: float
        :param max_effort: The max speed for which the robot to travel (Bounded from -1 to 1)
        :type max_effort: float
        :param timeout: The amount of time before the robot stops trying to turn and continues to the next step (In Seconds)
        :type timeout: float
        :param main_controller: The main controller, for handling the angle turned
        :type main_controller: Controller
        :param secondary_controller: The secondary controller, for maintaining position during the turn by controlling the encoder count difference
        :type secondary_controller: Controller
        :param use_imu: A boolean flag that changes if the main controller bases its movement off of the imu (True) or the encoders (False)
        :type use_imu: bool
        :return: if the distance was reached before the timeout
        :rtype: bool
        """

        if max_effort < 0:
            max_effort = -max_effort
            turn_degrees = -turn_degrees

        time_out = Timeout(timeout)
        starting_left = self.get_left_encoder_position()
        starting_right = self.get_right_encoder_position()

        if main_controller is None:
            main_controller = PID(
                # kp = 0.2,
                # ki = 0.004,
                # kd = 0.0036,
                kd = 0.0036 + 0.0034 * (max(max_effort, 0.5) - 0.5) * 2,
                kp = 0.2,
                ki = 0.004,
                #kd = 0.007,
                min_output = 0.1,
                max_output = max_effort,
                max_integral = 30,
                tolerance = 1,
                tolerance_count = 3
            )

        # Secondary controller to keep encoder values in sync
        if secondary_controller is None:
            secondary_controller = PID(
                kp = 0.25,
            )
 
        if use_imu and (self.imu is not None):
            turn_degrees += self.imu.get_yaw()

        while True:
            
            # calculate encoder correction to minimize drift
            left_delta = self.get_left_encoder_position() - starting_left
            right_delta = self.get_right_encoder_position() - starting_right
            encoder_correction = secondary_controller.update(left_delta + right_delta)

            if use_imu and (self.imu is not None):
                # calculate turn error (in degrees) from the imu
                turn_error = turn_degrees - self.imu.get_yaw()
            else:
                # calculate turn error (in degrees) from the encoder counts
                turn_error = turn_degrees - ((right_delta-left_delta)/2)*360/(self.track_width*math.pi)

            # Pass the turn error to the main controller to get a turn speed
            turn_speed = main_controller.update(turn_error)

            # exit if timeout or tolerance reached
            if main_controller.is_done() or time_out.is_done():
                break

            self.set_effort(-turn_speed - encoder_correction, turn_speed - encoder_correction)

            time.sleep(0.01)

        self.stop()

        return not time_out.is_done()

    def turn(self, degree, clockwise: bool = True, effort: float = 0.5) -> None:
        # Set the PID setpoint
        current_heading = self.GYRO.yaw()
        if clockwise:
            self.HEADING_SETPOINT = current_heading + degree
        else:
            self.HEADING_SETPOINT = current_heading - degree
        self.heading_pid.setSetpoint(self.HEADING_SETPOINT)
        # Check if the PID is at setpoint
        while not self.heading_pid.atSetpoint():
            # Not at setpoint so continue turning
            output = self.heading_pid.calculate(self.GYRO.yaw(), self.HEADING_SETPOINT)
            self.drive.tankDrive(output, -output)

    def wrap_angle(self, angle_in_radians: float) -> float:
        while angle_in_radians > math.pi:
            angle_in_radians -= 2 * math.pi
        while angle_in_radians < -math.pi:
            angle_in_radians += 2 * math.pi
        return angle_in_radians
    '''
    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    @magicbot.feedback(key="Distance")
    def distance(self) -> float:
        return (self.left_encoder_distance() + self.right_encoder_distance()) / 2.0

    @magicbot.feedback(key="Effort")
    def the_effort(self) -> float:
        return self.EFFORT

    @magicbot.feedback(key="Distance Setpoint")
    def the_distance_setpoint(self) -> float:
        return self.DISTANCE_SETPOINT

    @magicbot.feedback(key="Heading Setpoint")
    def the_heading_setpoint(self) -> float:
        return self.HEADING_SETPOINT

    @magicbot.feedback(key="Left Encoder Count")
    def left_encoder_count(self) -> int:
        return self.LEFT_ENCODER.get()

    @magicbot.feedback(key="Left Encoder Distance")
    def left_encoder_distance(self) -> float:
        return self.LEFT_ENCODER.getDistance()

    @magicbot.feedback(key="Right Encoder Count")
    def right_encoder_count(self) -> int:
        return self.RIGHT_ENCODER.get()

    @magicbot.feedback(key="Right Encoder Distance")
    def right_encoder_distance(self) -> float:
        return self.RIGHT_ENCODER.getDistance()

    """
    @magicbot.feedback(key="Wheel Speed")
    def wheel_speed(self) -> float:
        return wpimath.kinematics.DifferentialDriveWheelSpeeds(
            self.LEFT_ENCODER.getRate(), self.RIGHT_ENCODER.getRate()
        )
    """
