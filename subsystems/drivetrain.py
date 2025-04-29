# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
#

import math

import commands2
import wpilib
import xrp
import constants

from wpilib.drive import DifferentialDrive
from wpimath.kinematics import DifferentialDriveOdometry
from wpimath.geometry import Rotation2d, Pose2d
from wpilib import SmartDashboard


class Drivetrain(commands2.Subsystem):
    kCountsPerRevolution = (
        constants.ENCODER_RESOLUTION * constants.MOTOR_GEAR_RATIO
    )  # 585.0
    kWheelDiameterInch = constants.WHEEL_DIAMETER_INCH  # 2.3622

    def __init__(self) -> None:
        super().__init__()

        self.drive_mode = "arcade"  # default mode is arcade

        # The XRP has the left and right motors set to
        # PWM channels 0 and 1 respectively
        self.leftMotor = xrp.XRPMotor(constants.LEFT_MOTOR_CHANNEL)
        self.rightMotor = xrp.XRPMotor(constants.RIGHT_MOTOR_CHANNEL)
        self.rightMotor.setInverted(True)

        # The XRP has onboard encoders that are hardcoded
        # to use DIO pins 4/5 and 6/7 for the left and right
        self.leftEncoder = wpilib.Encoder(
            constants.LEFT_ENCODER_CHANNEL_A, constants.LEFT_ENCODER_CHANNEL_B
        )
        self.rightEncoder = wpilib.Encoder(
            constants.RIGHT_ENCODER_CHANNEL_A, constants.RIGHT_ENCODER_CHANNEL_B
        )

        # And an onboard gyro (and you have to power on your XRP when it is on flat surface)
        self.gyro = xrp.XRPGyro()
        self.accelerometer = wpilib.BuiltInAccelerometer()
        self.reflectanceSensor = xrp.XRPReflectanceSensor()
        self.distanceSensor = xrp.XRPRangefinder()

        # Use inches as unit for encoder distances
        self.leftEncoder.setDistancePerPulse(
            (math.pi * self.kWheelDiameterInch) / self.kCountsPerRevolution
        )
        self.rightEncoder.setDistancePerPulse(
            (math.pi * self.kWheelDiameterInch) / self.kCountsPerRevolution
        )
        self.resetEncoders()
        self.resetGyro()

        # Set up the differential drive controller and differential drive odometry
        self.drive = DifferentialDrive(self.leftMotor, self.rightMotor)
        self.odometry = DifferentialDriveOdometry(
            Rotation2d.fromDegrees(self.getGyroAngleZ()),
            self.getLeftDistanceInch(),
            self.getRightDistanceInch(),
        )

    def periodic(self) -> None:
        pose = self.odometry.update(
            Rotation2d.fromDegrees(self.getGyroAngleZ()),
            self.getLeftDistanceInch(),
            self.getRightDistanceInch(),
        )
        SmartDashboard.putNumber("x", pose.x)
        SmartDashboard.putNumber("y", pose.y)
        SmartDashboard.putNumber("z-heading", pose.rotation().degrees())
        SmartDashboard.putNumber("distance", self.getDistanceToObstacle())
        SmartDashboard.putNumber(
            "left-reflect", self.reflectanceSensor.getLeftReflectanceValue()
        )
        SmartDashboard.putNumber(
            "right-reflect", self.reflectanceSensor.getRightReflectanceValue()
        )

    def arcadeDrive(self, fwd: float, rot: float) -> None:
        """
        Drives the robot using arcade controls.

        :param fwd: the commanded forward movement
        :param rot: the commanded rotation
        """
        self.drive.arcadeDrive(fwd, -rot)

    def drive(self, a: float, b: float) -> None:
        """
        Drive the robot using the specified drive mode.

        :param a: the commanded forward movement or left movement
        :param b: the commanded rotation or right movement
        """
        if self.drive_mode == "arcade":
            self.arcadeDrive(a, b)
        elif self.drive_mode == "tank":
            self.tankDrive(a, b)

    def stop(self) -> None:
        """
        Stop the drivetrain motors
        """
        self.drive.arcadeDrive(0, 0)

    def tankDrive(self, left: float, right: float) -> None:
        """
        Drives the robot using tank controls.

        :param left: the commanded left movement
        :param right: the commanded right movement
        """
        self.drive.tankDrive(-left, -right)

    def resetEncoders(self) -> None:
        """Resets the drive encoders to currently read a position of 0."""
        self.leftEncoder.reset()
        self.rightEncoder.reset()

    def getLeftEncoderCount(self) -> int:
        return self.leftEncoder.get()

    def getRightEncoderCount(self) -> int:
        return self.rightEncoder.get()

    def getLeftDistanceInch(self) -> float:
        return -self.leftEncoder.getDistance()

    def getRightDistanceInch(self) -> float:
        return -self.rightEncoder.getDistance()

    def getAverageDistanceInch(self) -> float:
        """Gets the average distance of the TWO encoders."""
        return (self.getLeftDistanceInch() + self.getRightDistanceInch()) / 2.0

    def getAccelX(self) -> float:
        """The acceleration in the X-axis.

        :returns: The acceleration of the XRP along the X-axis in Gs
        """
        return self.accelerometer.getX()

    def getAccelY(self) -> float:
        """The acceleration in the Y-axis.

        :returns: The acceleration of the XRP along the Y-axis in Gs
        """
        return self.accelerometer.getY()

    def getAccelZ(self) -> float:
        """The acceleration in the Z-axis.

        :returns: The acceleration of the XRP along the Z-axis in Gs
        """
        return self.accelerometer.getZ()

    def getGyroAngleX(self) -> float:
        """Current angle of the XRP around the X-axis.

        :returns: The current angle of the XRP in degrees
        """
        return self.gyro.getAngleX()

    def getGyroAngleY(self) -> float:
        """Current angle of the XRP around the Y-axis.

        :returns: The current angle of the XRP in degrees
        """
        return self.gyro.getAngleY()

    def getGyroAngleZ(self) -> float:
        """Current angle of the XRP around the Z-axis.

        :returns: The current angle of the XRP in degrees
        """
        return self.gyro.getAngleZ()

    def getDistanceToObstacle(self, unit="inch") -> float:
        """Distance to obstacle in the front, as given by the distance sensor

        :returns: Distance in the requested unit.
        """
        distance = self.distanceSensor.getDistance()
        if unit == "inch" or unit == "in":
            return distance * 39.3701
        elif unit == "feet" or unit == "ft":
            return distance * 3.28084
        elif unit == "yard" or unit == "yd":
            return distance * 1.09361
        elif unit == "cm":
            return distance * 100
        elif unit == "meter":
            return distance
        else:
            raise ValueError(
                "Invalid unit. Use 'inch', 'feet', 'yard', 'cm', or 'meter'."
            )

    def resetGyro(self) -> None:
        """Reset the gyro"""
        self.gyro.reset()

    def resetOdometry(self, pose: Pose2d = Pose2d()) -> None:
        self.resetGyro()
        self.resetEncoders()
        heading = Rotation2d.fromDegrees(self.getGyroAngleZ())
        self.odometry.resetPosition(
            heading, self.getLeftDistanceInch(), self.getRightDistanceInch(), pose
        )
