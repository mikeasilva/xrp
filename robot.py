import autopilot
import constants
import components
import genie
import os
from wpimath.controller import PIDController

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
    turn_right: autopilot.TurnRight
    #turn_controller: PIDController

    ROTATE_TO_ANGLE = False

    def createObjects(self):
        self.controller_port = constants.CONTROLLER_PORT
        self.turn_controller = PIDController(
            constants.TURN_P, constants.TURN_I, constants.TURN_D
        )
        self.turn_controller.setTolerance(constants.TURN_TOLERANCE_DEGREES)
        self.turn_controller.enableContinuousInput(-180.0, 180.0)
    
    def disableInit(self):
        self.arm.set_position(0)

    def teleopInit(self):
        self.turn_controller.reset()

    def teleopPeriodic(self):
        # Blink to indicate telop mode
        self.led.blink(duration=0.1)
        self.controller.capture_buton_presses()

        # "Boost" the motor when the B button is pressed
        if self.controller.b_button_pressed():
            self.drivetrain.set_max_output(1)
        else:
            self.drivetrain.set_max_output(constants.DEFAULT_MAX_OUTPUT)

        # Get the input from the controller
        left_x, left_y, right_x, right_y = self.controller.get_joysticks()

        # Make adjustments based on the drive mode
        if self.drivetrain.mode == "arcade":
            left_stick = left_y
            right_stick = right_x
        else:
            # Using tank drive
            left_stick = -left_y
            right_stick = -right_y

        '''
        if self.ROTATE_TO_ANGLE:
            right_stick = self.turn_controller.calculate(self.drivetrain.imu.get_yaw())
            print(right_stick)
        if self.turn_controller.atSetpoint():
            self.ROTATE_TO_ANGLE = False
        '''
        # Use the controller input to move the robot
        self.drivetrain.go(left_stick, right_stick)

        if self.controller.x_button_was_pressed():
            #self.turn_controller.setSetpoint(-90.0)
            #self.ROTATE_TO_ANGLE = True
            print("X button was pressed")
            self.turn_right.engage()

        if self.controller.y_button_was_pressed():
            self.turn_right.disable()
            self.ROTATE_TO_ANGLE = False

        if self.controller.right_trigger_was_pressed():
            self.arm.set_position(0)

        if self.controller.left_trigger_was_pressed():
            self.arm.set_position(180)
