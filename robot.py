import constants
import components
import genie
import os

os.environ["HALSIMXRP_HOST"] = "192.168.42.1"
os.environ["HALSIMXRP_PORT"] = "3540"


class MyRobot(genie.GenieRobot):
    arm: components.Arm
    controller: components.XboxController
    controller_port: int
    distance_sensor: components.DistanceSensor
    drivetrain: components.Drivetrain
    led: components.LED
    line_sensor: components.LineSensor

    def createObjects(self):
        self.controller_port = constants.CONTROLLER_PORT

    def teleopPeriodic(self):
        # Blink to indicate telop mode
        self.led.blink(duration=0.1)
        self.controller.capture_buton_presses()

        if self.controller.x_button_was_pressed():
            print("X button was pressed")

        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()

        # Make adjustments based on the drive mode
        if self.drivetrain.mode == "arcade":
            left_stick = -left_y
            right_stick = -right_x
        else:
            # Using tank drive
            left_stick = -left_y
            right_stick = -right_y

        # Use the controller input to move the robot
        self.drivetrain.go(left_stick, right_stick)
