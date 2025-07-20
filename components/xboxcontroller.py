import wpilib
from magicbot import feedback


class XboxController:
    xbox_controller: wpilib.XboxController

    def execute(self) -> None:
        pass

    def setup(self):
        """
        Setup the Xbox controller.
        This method is called once when the robot is initialized.
        """
        self.correct_for_deadband = True
        self.deadband = 0.3

    def linear_deadband(self, raw_value: float, deadband: float) -> float:
        if abs(raw_value) < deadband:
            return 0.0
        return (raw_value / abs(raw_value)) * (
            (abs(raw_value) - deadband) / (1 - deadband)
        )

    @feedback(key="Left X")
    def get_left_x(self) -> float:
        """Get the X-axis value of the left joystick."""
        raw_value = self.xbox_controller.getLeftX()
        if self.correct_for_deadband:
            return self.linear_deadband(raw_value, self.deadband)
        return raw_value

    @feedback(key="Left Y")
    def get_left_y(self) -> float:
        """Get the Y-axis value of the left joystick."""
        raw_value = self.xbox_controller.getLeftY()
        if self.correct_for_deadband:
            return self.linear_deadband(raw_value, self.deadband)
        return raw_value

    @feedback(key="Right X")
    def get_right_x(self) -> float:
        """Get the X-axis value of the right joystick."""
        raw_value = self.xbox_controller.getRightX()
        if self.correct_for_deadband:
            return self.linear_deadband(raw_value, self.deadband)
        return raw_value

    @feedback(key="Right Y")
    def get_right_y(self) -> float:
        """Get the Y-axis value of the right joystick."""
        raw_value = self.xbox_controller.getRightY()
        if self.correct_for_deadband:
            return self.linear_deadband(raw_value, self.deadband)
        return raw_value

    def get_joysticks(self) -> tuple[float, float, float, float]:
        """
        Get the joystick values from the Xbox controller.

        :return: A tuple containing the left joystick x, left joystick y, right joystick x, and right joystick y values.
        """
        self.left_joystick_x = self.xbox_controller.getLeftX()
        self.left_joystick_y = self.xbox_controller.getLeftY()
        self.right_joystick_x = self.xbox_controller.getRightX()
        self.right_joystick_y = self.xbox_controller.getRightY()
        return (
            self.left_joystick_x,
            self.left_joystick_y,
            self.right_joystick_x,
            self.right_joystick_y,
        )

    def a_button_pressed(self) -> bool:
        """
        Check if the A button is pressed.

        :return: True if the A button is pressed, False otherwise.
        """
        return self.xbox_controller.getAButton()

    def b_button_pressed(self) -> bool:
        """
        Check if the B button is pressed.
        :return: True if the B button is pressed, False otherwise.
        """
        return self.xbox_controller.getBButton()

    def x_button_pressed(self) -> bool:
        """
        Check if the X button is pressed.

        :return: True if the X button is pressed, False otherwise.
        """
        return self.xbox_controller.getXButton()

    def y_button_pressed(self) -> bool:
        """
        Check if the Y button is pressed.

        :return: True if the Y button is pressed, False otherwise.
        """
        return self.xbox_controller.getYButton()

    def dpad_up_pressed(self) -> bool:
        """
        Check if the D-pad is pressed up.

        :return: True if the D-pad is pressed up, False otherwise.
        """
        return self.xbox_controller.getPOV() == 0

    def dpad_down_pressed(self) -> bool:
        """
        Check if the D-pad is pressed down.

        :return: True if the D-pad is pressed down, False otherwise.
        """
        return self.xbox_controller.getPOV() == 180

    def dpad_left_pressed(self) -> bool:
        """
        Check if the D-pad is pressed left.

        :return: True if the D-pad is pressed left, False otherwise.
        """
        return self.xbox_controller.getPOV() == 270

    def dpad_right_pressed(self) -> bool:
        """
        Check if the D-pad is pressed right.

        :return: True if the D-pad is pressed right, False otherwise.
        """
        return self.xbox_controller.getPOV() == 90

    def left_bumper_pressed(self) -> bool:
        """
        Check if the left bumper is pressed.

        :return: True if the left bumper is pressed, False otherwise.
        """
        return self.xbox_controller.getLeftBumper()

    def right_bumper_pressed(self) -> bool:
        """
        Check if the right bumper is pressed.

        :return: True if the right bumper is pressed, False otherwise.
        """
        return self.xbox_controller.getRightBumper()

    def left_trigger_pressed(self) -> float:
        """
        Get the value of the left trigger.

        :return: The value of the left trigger, ranging from 0.0 to 1.0.
        """
        return self.xbox_controller.getLeftTriggerAxis()

    def right_trigger_pressed(self) -> float:
        """
        Get the value of the right trigger.

        :return: The value of the right trigger, ranging from 0.0 to 1.0.
        """
        return self.xbox_controller.getRightTriggerAxis()

    def start_button_pressed(self) -> bool:
        """
        Check if the start button is pressed.

        :return: True if the start button is pressed, False otherwise.
        """
        return self.xbox_controller.getStartButton()

    def back_button_pressed(self) -> bool:
        """
        Check if the back button is pressed.

        :return: True if the back button is pressed, False otherwise.
        """
        return self.xbox_controller.getBackButton()
