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
import time
import wpilib
import json

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

        with open("log.txt", "w") as f:
            f.write("LOG STARTED\n")

        # Read in the joystick drift
        try:
            with open("joystick_drift.json", "r") as f:
                self.joystick_drift = json.load(f)
        except:
            self.joystick_drift = {
                "left": 0.0,
                "right": 0.0,
            }

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
            and self._get_left_stick_y() < 0
        ):
            # We need to stop this wreckless behavior
            self.drivetrain.stop()
        else:
            # Drive the robot using the controller
            self.drivetrain.drive(
                self._get_left_stick_y(), self._get_right_stick_x()
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
            elif dpad == 90:
                # Right button on D-pad pressed so turn right on the left wheel
                self.drivetrain.drive_mode = "tank"
                self.drivetrain.drive(-1, 0)
            elif dpad == 270:
                # Left button on D-pad pressed so turn left on the right wheel
                self.drivetrain.drive_mode = "tank"
                self.drivetrain.drive(0, -1)
            self.drivetrain.drive_mode = "arcade"

    """
    ====================================================================
    Test mode functions
    ====================================================================
    """

    def testInit(self) -> None:
        print("Test Mode")
        self.led.off()
        self.drivetrain.stop()
        with open("log.txt", "a") as f:
            f.write("test\n")
        self.n_test = 0
        self.test_results = {}
        self.test = "Left Up Test"

    def testPeriodic(self) -> None:
        if self.n_test == 41:
                with open("joystick_calibration.json", "w") as f:
                    json.dump(self.test_results, f, indent=4)
                print("Joystick calibration data saved to joystick_calibration.json")

                drift = {}
                x = 0
                i = 0
                for key in ["left_stick_up", "left_stick_down"]:
                    for item in self.test_results[key]:
                        x += item
                        i += 1

                drift["left"] = -(x / i)

                x = 0
                i = 0
                for key in ["right_stick_right", "right_stick_left"]:
                    for item in self.test_results[key]:
                        x += item
                        i += 1

                drift["right"] = -(x / i)

                with open("joystick_drift.json", "w") as f:
                    json.dump(drift, f, indent=4)


                self.n_test += 1
        elif self.n_test == 42:
            pass
        else:    
            print(self.test + ":" + str(self.n_test))
            if self.controller.getAButtonPressed():
                left = self.controller.getLeftY()
                right = self.controller.getRightX()
                if self.n_test < 11:
                    result = left
                    key = "left_stick_up"
                elif self.n_test < 21:
                    result = left
                    key = "left_stick_down"
                elif self.n_test < 31:
                    result = right
                    key = "right_stick_right"
                elif self.n_test < 41:
                    result = right
                    key = "right_stick_left"

                results = self.test_results.get(key, [])
                results.append(result)
                self.test_results[key] = results
                self.n_test += 1

                if self.n_test == 10:
                    self.test = "Left Down Test"
                elif self.n_test == 20:
                    self.test = "Right Right Test"
                elif self.n_test == 30:
                    self.test = "Right Left Test"

    """
    ====================================================================
    Miscellaneous functions
    ====================================================================
    """

    def robotPeriodic(self) -> None:
        pass

    def simulationPeriodic(self) -> None:
        pass

    def _get_left_stick_y(self) -> float:
        """
        Get the left stick Y value from the controller.
        """
        return self.controller.getLeftY() + self.joystick_drift["left"]
    
    def _get_right_stick_x(self) -> float:
        """
        Get the right stick X value from the controller.
        """
        return self.controller.getRightX() + self.joystick_drift["right"]
