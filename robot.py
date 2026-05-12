# XRP MagicBot
# To Run: robotpy sim --xrp

import components
import constants
import magicbot
import math
import os
import wpilib
import xrp

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    # Magicbot components
    controller: components.XboxController
    gyro: components.XRPGyro
    led: components.XRPLed
    servo: components.XRPServo
    drivetrain: components.XRPTankDrive
    rangefinder: components.XRPRangefinder
    reflectance_sensor: components.XRPReflectanceSensor

    def createObjects(self):
        if constants.LOGGING_ENABLED:
            wpilib.DataLogManager.start()
            self.log = wpilib.DataLogManager.getLog()

        self.name = constants.Robot.NAME
        self.servo_change = constants.Robot.SERVO_CHANGE
        self.cruise_control_enabled = False
        self.cruise_control_speed = 0.0
        self.current_state = "CREATING OBJECTS"

        self.controller_port = constants.Ids.CONTROLLER

        gyro = xrp.XRPGyro()
        self.gyro_noise_threshold = constants.Robot.GYRO_NOISE_THRESHOLD

        self.odometry_gyro = gyro

        self.servo_channel = constants.Ids.SERVO

        # Set up the motors
        left_motor = xrp.XRPMotor(constants.Ids.LEFT_MOTOR)
        left_motor.setSafetyEnabled(True)
        right_motor = xrp.XRPMotor(constants.Ids.RIGHT_MOTOR)
        right_motor.setSafetyEnabled(True)
        right_motor.setInverted(True)
        self.drivetrain_left_motor = left_motor
        self.drivetrain_right_motor = right_motor

        # Set up the encoders
        right_encoder = wpilib.Encoder(*constants.Ids.RIGHT_ENCODER)
        left_encoder = wpilib.Encoder(*constants.Ids.LEFT_ENCODER)
        # Distance per pulse is pi * wheel diameter / pulses per revolution * gear ratio
        distance_per_pulse = (
            math.pi
            * constants.Robot.WHEEL_DIAMETER_M
            / (constants.Robot.PULSES_PER_REVOLUTION * constants.Robot.GEAR_RATIO)
        )
        right_encoder.setDistancePerPulse(distance_per_pulse)
        right_encoder.setReverseDirection(True)
        left_encoder.setDistancePerPulse(distance_per_pulse)
        self.drivetrain_right_encoder = right_encoder
        self.drivetrain_left_encoder = left_encoder

        self.drivetrain_control_style = constants.Robot.DEFAULT_DRIVETRAIN_CONTROL_STYLE

        # PID settings for the drivetrain
        self.drivetrain_distance_pid_values = constants.PID.DISTANCE
        self.drivetrain_heading_pid_values = constants.PID.HEADING

        self.led_blink_time = constants.LED_BLINK_TIME

    def autonomousInit(self):
        self.current_state = "AUTONOMOUS"
        self.led.mode = "on"

    def disabledPeriodic(self):
        self.current_state = "DISABLED"
        self.led.mode = "off"
        self.drivetrain.stop()

    def teleopInit(self):
        self.current_state = "TELEOP INIT"
        self.led.mode = "blink"

    def teleopPeriodic(self):
        if self.drivetrain_control_style == "tank":
            self.drivetrain.drive(
                left_speed=-self.controller.left_y, right_speed=-self.controller.right_y
            )
        else:
            # Cruise Control Check
            if self.cruise_control_enabled:
                self.current_state = "CRUISE CONTROL ENABLED"
                speed = self.cruise_control_speed
            else:
                self.current_state = "HUMAN CONTROLLED"
                speed = -self.controller.left_y

            # Crash Avoidance: Stop the robot if an object is too close
            if self.rangefinder.distance <= constants.Robot.CRASH_AVOIDANCE_THRESHOLD:
                self.current_state = "CRASH AVOIDANCE"
                speed = 0.0

            self.drivetrain.drive(speed, -self.controller.right_x)

        # Servo control with bumpers
        ## Left bumper raises the servo, right bumper lowers it
        if self.controller.left_bumper_pressed():
            self.servo.position += self.servo_change
        elif self.controller.right_bumper_pressed():
            self.servo.position -= self.servo_change

        # Enable/disable cruise control with the Y button
        if self.controller.y_button_was_pressed():
            # Toggle cruise control
            self.cruise_control_enabled = not self.cruise_control_enabled
            # Set the cruise control speed if it's enabled
            if self.cruise_control_enabled:
                self.cruise_control_speed = speed

    @magicbot.feedback(key="name")
    def get_name(self) -> str:
        return self.name

    @magicbot.feedback(key="is")
    def get_current_state(self):
        """Return the current state of the robot"""
        return self.current_state

    @magicbot.feedback(key="cruise control enabled")
    def get_cruise_control_enabled(self) -> bool:
        return self.cruise_control_enabled

    @magicbot.feedback
    def pose(self):
        return [
            0.0,  # self.localizer.pose.X,
            0.0,  # self.localizer.pose.Y,
            self.gyro.angle,
        ]
