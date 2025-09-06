import constants
from magicbot import feedback
import subsystems
#from wpilib.system import sysid
import wpimath.geometry
from wpimath.kinematics import DifferentialDriveOdometry

class Drivetrain:
    #DISTANCE_TIME_SERIES = [0.0, 0.0, 0.0, 0.0, 0.0]#, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    PREV_DISTANCE = 0.0
    PREV_TIME = 0.0
    IS_MOVING = False
    HEADING = 0.0

    def setup(self):
        self.drivetrain = subsystems.XRPDrivetrain()
        self.imu = subsystems.XRPGyro()
        self.imu.reset()
        self.HEADING = self.imu.get_yaw()
        self.mode = "arcade"  # or "tank"
        self.max_output = constants.DEFAULT_MAX_OUTPUT
        self.drivetrain.set_drive_mode(self.mode)
        self.odometry = DifferentialDriveOdometry(
            self.imu.get_rotation2d(), self.drivetrain.get_left_encoder_position(units="m"), self.drivetrain.get_right_encoder_position(units="m")
        )
        
        '''
        # SystemID setup
        self.sysid_logger = sysid.SysIdRoutine(
            config=sysid.SysIdRoutine.Config(
                fast=True  # Use True for dynamic tests, False for quasistatic
            ),
            motor_voltage_func=self._apply_volts,
            log_func=self._log_telemetry
        )

    def _apply_volts(self, volts: sysid.SysIdRoutine.VoltageCommand):
        # Convert voltage to PWM percent [-1.0, 1.0]
        scale = 1.0 / 12.0
        self.drivetrain.set_left_motor(volts.left * scale)
        self.drivetrain.set_right_motor(volts.right * scale)

    def _log_telemetry(self, log: sysid.SysIdRoutine.TelemetryData):
        # Log voltage, position, velocity
        log.motor_voltage = (
            self.drivetrain.get_left_motor_voltage(),
            self.drivetrain.get_right_motor_voltage()
        )
        log.motor_position = (
            self.drivetrain.get_left_encoder_position(),
            self.drivetrain.get_right_encoder_position()
        )
        log.motor_velocity = (
            self.drivetrain.get_left_encoder_velocity(),
            self.drivetrain.get_right_encoder_velocity()
        )
    '''

    def execute(self):
        '''
        # Get the current speed of the robot
        distance = self.drivetrain.get_distance_traveled()
        self.drivetrain.reset_encoders()
        # Update the time series
        self.DISTANCE_TIME_SERIES.pop(0)
        self.DISTANCE_TIME_SERIES.append(distance)
        '''
        pass

    @feedback(key="X")
    def get_x(self) -> float:
        return round(self.imu.get_x(), 2)

    @feedback(key="Y")
    def get_y(self) -> float:
        return round(self.imu.get_y(), 2)

    
    def get_z(self) -> float:
        return round(self.imu.get_z(), 1)

    @feedback(key="Robot Pose")
    def get_pose_string(self) -> str:
        pose = self.odometry.getPose()
        return f"({pose.X():.2f}, {pose.Y():.2f}) @ {pose.rotation().degrees():.2f} deg"

    @feedback(key="Heading")
    def get_heading(self) -> float:
        """
        Get the current heading of the robot in degrees.
        :return: The current heading in degrees.
        """
        if not self.IS_MOVING:
            # This is the core ZUPT step
            # Reset the gyroscope yaw reading to zero to eliminate drift
            # Or, if using odometry, you can set the heading directly
            #self.imu.reset()
                
            # You might also want to reset the odometry pose's rotation
            # to the corrected gyro value.
            # Here, we can create a new pose with the current position but corrected heading
            corrected_pose = wpimath.geometry.Pose2d(self.odometry.getPose().X(), self.odometry.getPose().Y(), wpimath.geometry.Rotation2d(0))
            #self.odometry.resetPose(corrected_pose)
        
        pose = self.odometry.getPose()
        self.HEADING = round(pose.rotation().degrees(), 1)
        return self.HEADING
    
    def go(self, forward: float, rotation: float) -> None:
        """
        Move the robot using arcade drive.
        :param forward: The forward/backward speed (-1 to 1).
        :param rotation: The rotation speed (-1 to 1).
        """
        self.drivetrain.drive(forward * self.max_output, rotation * self.max_output)

    def set_max_output(self, max_output) -> None:
        """
        Set the maximum output for the drivetrain motors.
        :param max_output: The maximum output value (0 to 1).
        """
        if max_output < 0 or max_output > 1:
            raise ValueError("Max output must be between 0 and 1")
        self.max_output = max_output

    def stop(self) -> None:
        """
        Stop the robot.
        """
        self.drivetrain.stop()

    @feedback(key="Moving")
    def get_is_moving(self) -> bool:
        self.IS_MOVING = (round(abs(self.drivetrain.left_motor.get()), 1) != 0) or (round(abs(self.drivetrain.right_motor.get()), 1) != 0)
        return self.IS_MOVING