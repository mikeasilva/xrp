"""XRP Robot."""

import math
import os

import magicbot
import wpilib
import xrp

import components
import constants

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(magicbot.MagicRobot):
    controller: components.XboxController
    gyro: components.Gyro
    drivetrain: components.SmoothDrive

    def create_objects(self):
        self.name = constants.Robot.NAME
        self.controller_port = constants.Ids.CONTROLLER
        self.gyro_type = "xrp"
        # Setup the drivetrain
        self.drivetrain_type = "tank"
        self.drivetrain_max_speed_mps = constants.Robot.MAX_SPEED_MPS
        self.drivetrain_max_speed_normal = constants.Robot.NORMAL_SPEED_MPS
        self.drivetrain_max_speed_boost = constants.Robot.BOOST_SPEED_MPS
        self.drivetrain_max_speed_precision = constants.Robot.PRECISION_SPEED_MPS
        self.drivetrain_track_width = constants.Robot.TRACK_WIDTH_M
        ## Set up the motors and encoders
        left_motor = xrp.XRPMotor(constants.Ids.LEFT_MOTOR)
        right_motor = xrp.XRPMotor(constants.Ids.RIGHT_MOTOR)
        right_motor.set_inverted(True)
        right_encoder = wpilib.Encoder(*constants.Ids.RIGHT_ENCODER)
        left_encoder = wpilib.Encoder(*constants.Ids.LEFT_ENCODER)
        ### Distance per pulse is pi * wheel diameter / pulses per revolution * gear ratio
        distance_per_pulse = (
            math.pi
            * constants.Robot.WHEEL_DIAMETER_M
            / (constants.Robot.PULSES_PER_REVOLUTION * constants.Robot.GEAR_RATIO)
        )
        right_encoder.set_distance_per_pulse(distance_per_pulse)
        right_encoder.set_reverse_direction(True)
        left_encoder.set_distance_per_pulse(distance_per_pulse)
        self.drivetrain_components = {
            "left_motor": left_motor,
            "right_motor": right_motor,
            "left_encoder": left_encoder,
            "right_encoder": right_encoder,
        }

    def disabled_periodic(self):
        pass

    def teleop_init(self):
        self.gyro.reset()
        self.drivetrain.reset()

    def teleop_periodic(self):
        # Change the drive "mode" based on the bumpers. Boost mode is faster, precision mode is slower.
        if self.controller.right_bumper_pressed():
            self.drivetrain.set_mode("boost")
        elif self.controller.left_bumper_pressed():
            self.drivetrain.set_mode("precision")
        else:
            self.drivetrain.set_mode("normal")
        # Pass controller inputs to the drivetrain. Forward is left stick Y, rotation is right stick X.
        self.drivetrain.drive(
            fwd=-self.controller.left_y,
            rot=-self.controller.right_x,
        )
