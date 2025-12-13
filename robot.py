import components
import constants
import genie
import os
#import state_machines
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class Robot(genie.GenieRobot):
    ACCELEROMETER: components.Accelerometer
    CONTROLLER: components.XboxController
    DISTANCE_SENSOR: components.DistanceSensor
    #drive_straight: state_machines.DriveStraight
    DRIVETRAIN: components.DriveTrain
    GYRYO: components.Gyro
    #HUSKYLENS: components.HuskyLens
    LED: components.LED
    REFLECTANCE_SENSOR: components.ReflectanceSensor
    SERVO: components.Servo

    def createObjects(self):
        # Controller stuff here
        self.CONTROLLER_CORRECT_FOR_DEADBAND = True
        self.CONTROLLER_DEADBAND = constants.CONTROLLER_DEADBAND
        self.CONTROLLER_PORT = constants.CONTROLLER_PORT

        # Drivetrain stuff here
        self.DRIVETRAIN_LEFT_MOTOR = xrp.XRPMotor(constants.LEFT_MOTOR_DEVICE_NUMBER)
        self.DRIVETRAIN_LEFT_ENCODER = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL[0], constants.LEFT_ENCODER_CHANNEL[1]
        )
        self.DRIVETRAIN_RIGHT_MOTOR = xrp.XRPMotor(constants.RIGHT_MOTOR_DEVICE_NUMBER)
        self.DRIVETRAIN_RIGHT_MOTOR.setInverted(True)
        self.DRIVETRAIN_RIGHT_ENCODER = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL[0], constants.RIGHT_ENCODER_CHANNEL[1]
        )
        self.DRIVETRAIN_ENCODER_UNITS = constants.ENCODER_UNITS

        # PID values for the drivetrain
        self.DRIVETRAIN_DISTANCE_PID_P = constants.DISTANCE_PID[0]
        self.DRIVETRAIN_DISTANCE_PID_I = constants.DISTANCE_PID[1]
        self.DRIVETRAIN_DISTANCE_PID_D = constants.DISTANCE_PID[2]
        
        self.DRIVETRAIN_HEADING_PID_P = constants.HEADING_PID[0]
        self.DRIVETRAIN_HEADING_PID_I = constants.HEADING_PID[1]
        self.DRIVETRAIN_HEADING_PID_D = constants.HEADING_PID[2]

        # Distance Sensor
        self.DISTANCE_SENSOR_UNIT = constants.DISTANCE_SENSOR_UNIT

        # Gyro - Passed into the gyro and accelerometer components
        self.XRP_GYRO = xrp.XRPGyro()

        # HuskyLens AI Camera
        self.HUSKYLENS_DEFAULT_ALGORITHM = constants.HUSKYLENS_DEFAULT_ALGORITHM

        # Servo
        self.SERVO_CHANNEL = constants.SERVO_CHANNEL

        if constants.LOGGING_ENABLED:
            wpilib.DataLogManager.start()
            wpilib.DriverStation.startDataLog(wpilib.DataLogManager.getLog())

    def autonomousInit(self) -> None:
        self.LED.turn_on()
        return super().autonomousInit()

    def disabledInit(self) -> None:
        self.LED.turn_off()
        self.SERVO.set_position(0)
        return super().disabledInit()
        

    def teleopPeriodic(self) -> None:
        self.LED.blink()
        self.CONTROLLER.capture_button_presses()
        left_x, left_y, right_x, right_y = self.CONTROLLER.get_joysticks()
        self.DRIVETRAIN.arcade_drive(-left_y, -right_x)
        
        if self.CONTROLLER.y_button_was_pressed():
            self.DRIVETRAIN.straight(12, "inches")
        '''
        if self.CONTROLLER.dpad_right_was_pressed():
            self.DRIVETRAIN.turn(90)

        if self.CONTROLLER.dpad_left_was_pressed():
            self.DRIVETRAIN.turn(-90)
        '''
        if self.CONTROLLER.b_button_pressed():
            self.DRIVETRAIN.set_effort(1)
        else:
            self.DRIVETRAIN.set_effort(0.8)
