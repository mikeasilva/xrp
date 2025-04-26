#!/usr/bin/env python3
#
# Run the program
# ---------------
# python -m robotpy sim --xrp
#
# To run the robot tests
# ---------------
# python -m robotpy test

import os
import random
import constants
from subsystems.arm import Arm
from subsystems.drivetrain import Drivetrain
from subsystems.gyro import Gyro
from subsystems.led import LED
from subsystems.networktables import NetworkTables
from subsystems.sensors import DistanceSensor, LineSensor
import wpilib

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyXRP(wpilib.TimedRobot):
    def robotInit(self) -> None:
        """
        This function is run when the robot is first started up and should be used for any
        initialization code.
        """
        print("Robot Init")
        # Initialize the robot
        self.arm = Arm()
        self.controller = wpilib.XboxController(constants.CONTROLLER_PORT)
        self.distance_sensor = DistanceSensor()
        self.drivetrain = Drivetrain(constants.DRIVE_MODE)
        self.gyro = Gyro()
        self.led = LED()
        self.line_sensor = LineSensor()
        self.network_tables = NetworkTables()

        # Reset components
        self.gyro.reset()
        self.drivetrain.reset_encoders()
        self.arm.set_position(0.0)

        # Get the current state of the robot
        self._get_current_state()

    def _get_current_state(self) -> None:
        """
        Get the current state of the robot.
        """
        self.current_arm_position = self.arm.get_position()
        self.current_distance = self.distance_sensor.get_distance()
        self.current_gyro_z = self.gyro.get_z()
        self.current_left_line_sensor = self.line_sensor.get_left_sensor()
        self.current_right_line_sensor = self.line_sensor.get_right_sensor()

        print(
            f"""Current State
            arm position: {self.current_arm_position}
            distance: {self.current_distance}
            z: {self.current_gyro_z}
            left line sensor: {self.current_left_line_sensor}
            right line sensor: {self.current_right_line_sensor}
            """
        )

    """
    ====================================================================
    Autonomous mode functions
    ====================================================================
    """

    def autonomousInit(self) -> None:
        print("Autonomous Mode")
        self.led.on()
        # self.drivetrain.safe(True)

    def autonomousPeriodic(self) -> None:
        distance_to_nearest_object = self.distance_sensor.get_distance()

        if distance_to_nearest_object - constants.CRASH_AVOIDANCE_DISTANCE > 0:
            # If the distance is greater than the crash avoidance distance, drive forward
            self.drivetrain.drive(-0.75, 0)
            print(f"Distance: {distance_to_nearest_object}")
        else:
            self.drivetrain.stop()
            current_heading = self.gyro.get_z()
            change_by = random.uniform(45, 315)
            if random.randint(0, 1) == 0:
                print("Turning left")
                turn_to = round(current_heading - change_by, 0)
                turn_by = 0.75
            else:
                print("Turning right")
                turn_to = round(current_heading + change_by, 0)
                turn_by = -0.75
            """
            while True:
                if round(self.gyro.get_z, 0) >= turn_to:
                    break
                self.drivetrain.drive(0, turn_by)
            """

    """
    ====================================================================
    Disabled mode functions
    ====================================================================
    """

    def disabledInit(self) -> None:
        print("Disabled Mode")
        self.led.off()
        self.drivetrain.stop()

    def disabledPeriodic(self):
        pass

    """
    ====================================================================
    Teleop mode functions
    ====================================================================
    """

    def teleopInit(self) -> None:
        print("Teleop Mode")

    def teleopPeriodic(self) -> None:
        # Blink the LED to indicate that the robot is in teleop mode
        self.led.blink()
        distance_to_nearest_object = self.distance_sensor.get_distance()

        # Crash avoidance system
        # Check if the distance to the nearest object is under the crash avoidance threshold
        # and the user is trying to move the robot foward
        if (
            distance_to_nearest_object <= constants.CRASH_AVOIDANCE_DISTANCE
            and self.controller.getLeftY() < 0
        ):
            # We need to stop this wreckless behavior
            self.drivetrain.stop()
        else:
            # Drive the robot using the controller
            self.drivetrain.drive(
                self.controller.getLeftY(), self.controller.getRightX()
            )

        # Display information about the robot on the console
        if self.controller.getAButtonPressed():
            self._get_current_state()
        # Read the D-pad value and move the arm accordingly
        dpad = self.controller.getPOV()
        if dpad != -1:
            shift_by = constants.ARM_SERVO_SHIFT_BY
            if dpad == 0:
                # Up button on D-pad pressed so move the arm up
                self.arm.set_position(self.arm.get_position() + shift_by)
            elif dpad == 180:
                # Down button on D-pad pressed so move the arm down
                self.arm.set_position(self.arm.get_position() + (-1 * shift_by))

    """
    ====================================================================
    Test mode functions
    ====================================================================
    """

    def testInit(self) -> None:
        print("Test Mode")
        self.led.off()
        self.effort = 0
        self.drivetrain.stop()

    def testPeriodic(self) -> None:
        pass

    """
    ====================================================================
    Miscellaneous functions
    ====================================================================
    """

    def robotPeriodic(self) -> None:
        pass

    def simulationPeriodic(self) -> None:
        pass
