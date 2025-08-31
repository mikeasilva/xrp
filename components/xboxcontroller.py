import wpilib
from magicbot import feedback


class XboxController:
    port: int

    def execute(self) -> None:
        pass

    def setup(self):
        """
        Setup the Xbox controller.
        This method is called once when the robot is initialized.
        """
        self.correct_for_deadband = True
        self.deadband = 0.3
        self.xbox_controller = wpilib.XboxController(self.port)
        self.button_pressed = {
            "A": False,
            "B": False,
            "X": False,
            "Y": False,
            "DPad_Up": False,
            "DPad_Down": False,
            "DPad_Left": False,
            "DPad_Right": False,
            "Left_Bumper": False,
            "Right_Bumper": False,
            "Left_Trigger": False,
            "Right_Trigger": False,
            "Start": False,
            "Back": False,
        }

    def _button_pressed(self, button_name: str, pressed: bool) -> bool:
        """
        Generic method to check if a button is pressed.
        :param button_name: The name of the button to check.
        :param pressed: The current state of the button (True if pressed, False otherwise).
        """
        if pressed:
            self.button_pressed[button_name] = True
        return pressed

    def _button_was_pressed(self, button_name: str) -> bool:
        """
        Generic method to check if a button was pressed since the last check.
        :param button_name: The name of the button to check.
        :return: True if the button was pressed since the last check, False otherwise.
        """
        if self.button_pressed[button_name]:
            self.button_pressed[button_name] = False
            return True
        return False

    def _corrected_joystick_value(self, raw_value: float) -> float:
        """
        Apply deadband correction to a joystick value.
        :param raw_value: The raw joystick value.
        :return: The corrected joystick value.
        """
        if self.correct_for_deadband:
            if abs(raw_value) < self.deadband:
                return 0.0
            return (raw_value / abs(raw_value)) * (
                (abs(raw_value) - self.deadband) / (1 - self.deadband)
            )
        return raw_value

    def get_joysticks(self) -> tuple[float, float, float, float]:
        """
        Get the joystick values from the Xbox controller.

        :return: A tuple containing the left joystick x, left joystick y, right joystick x, and right joystick y values.
        """
        return (
            self._corrected_joystick_value(self.xbox_controller.getLeftX()),
            self._corrected_joystick_value(self.xbox_controller.getLeftY()),
            self._corrected_joystick_value(self.xbox_controller.getRightX()),
            self._corrected_joystick_value(self.xbox_controller.getRightY()),
        )

    def a_button_pressed(self) -> bool:
        """
        Check if the A button is pressed.

        :return: True if the A button is pressed, False otherwise.
        """
        return self._button_pressed("A", self.xbox_controller.getAButton())

    def a_button_was_pressed(self) -> bool:
        """
        Check if the A button was pressed since the last check.

        :return: True if the A button was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("A")

    def b_button_pressed(self) -> bool:
        """
        Check if the B button is pressed.
        :return: True if the B button is pressed, False otherwise.
        """
        return self._button_pressed("B", self.xbox_controller.getBButton())

    def b_button_was_pressed(self) -> bool:
        """
        Check if the B button was pressed since the last check.

        :return: True if the B button was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("B")

    def x_button_pressed(self) -> bool:
        """
        Check if the X button is pressed.

        :return: True if the X button is pressed, False otherwise.
        """
        return self._button_pressed("X", self.xbox_controller.getXButton())

    def x_button_was_pressed(self) -> bool:
        """
        Check if the X button was pressed since the last check.

        :return: True if the X button was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("X")

    def y_button_pressed(self) -> bool:
        """
        Check if the Y button is pressed.

        :return: True if the Y button is pressed, False otherwise.
        """
        return self._button_pressed("Y", self.xbox_controller.getYButton())

    def y_button_was_pressed(self) -> bool:
        """
        Check if the Y button was pressed since the last check.

        :return: True if the Y button was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Y")

    def dpad_up_pressed(self) -> bool:
        """
        Check if the D-pad is pressed up.

        :return: True if the D-pad is pressed up, False otherwise.
        """
        return self._button_pressed("DPad_Up", self.xbox_controller.getPOV() == 0)

    def dpad_up_was_pressed(self) -> bool:
        """
        Check if the D-pad was pressed up since the last check.

        :return: True if the the D-pad was pressed up since the last check, False otherwise.
        """
        return self._button_was_pressed("DPad_Up")

    def dpad_down_pressed(self) -> bool:
        """
        Check if the D-pad is pressed down.

        :return: True if the D-pad is pressed down, False otherwise.
        """
        return self._button_pressed("DPad_Down", self.xbox_controller.getPOV() == 180)

    def dpad_down_was_pressed(self) -> bool:
        """
        Check if the D-pad was pressed down since the last check.

        :return: True if the the D-pad was pressed down since the last check, False otherwise.
        """
        return self._button_was_pressed("DPad_Down")

    def dpad_left_pressed(self) -> bool:
        """
        Check if the D-pad is pressed left.

        :return: True if the D-pad is pressed left, False otherwise.
        """
        return self._button_pressed("DPad_Left", self.xbox_controller.getPOV() == 270)

    def dpad_left_was_pressed(self) -> bool:
        """
        Check if the D-pad was pressed left since the last check.

        :return: True if the the D-pad was pressed left since the last check, False otherwise.
        """
        return self._button_was_pressed("DPad_Left")

    def dpad_right_pressed(self) -> bool:
        """
        Check if the D-pad is pressed right.

        :return: True if the D-pad is pressed right, False otherwise.
        """
        return self._button_pressed("DPad_Right", self.xbox_controller.getPOV() == 90)

    def dpad_right_was_pressed(self) -> bool:
        """
        Check if the D-pad was pressed right since the last check.

        :return: True if the the D-pad was pressed right since the last check, False otherwise.
        """
        return self._button_was_pressed("DPad_Right")

    def left_bumper_pressed(self) -> bool:
        """
        Check if the left bumper is pressed.

        :return: True if the left bumper is pressed, False otherwise.
        """
        return self._button_pressed("Left_Bumper", self.xbox_controller.getLeftBumper())

    def left_bumper_was_pressed(self) -> bool:
        """
        Check if the left bumper was pressed since the last check.

        :return: True if the left bumper was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Left_Bumper")

    def right_bumper_pressed(self) -> bool:
        """
        Check if the right bumper is pressed.

        :return: True if the right bumper is pressed, False otherwise.
        """
        return self._button_pressed(
            "Right_Bumper", self.xbox_controller.getRightBumper()
        )

    def right_bumper_was_pressed(self) -> bool:
        """
        Check if the right bumper was pressed since the last check.

        :return: True if the right bumper was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Right_Bumper")

    def left_trigger_pressed(self) -> float:
        """
        Get the value of the left trigger.

        :return: The value of the left trigger, ranging from 0.0 to 1.0.
        """
        self._button_pressed(
            "Left_Trigger", self.xbox_controller.getLeftTriggerAxis() >= 0.5
        )
        return self.xbox_controller.getLeftTriggerAxis()

    def left_trigger_was_pressed(self) -> bool:
        """
        Check if the left trigger was pressed since the last check.

        :return: True if the left trigger was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Left_Trigger")

    def right_trigger_pressed(self) -> float:
        """
        Get the value of the right trigger.

        :return: The value of the right trigger, ranging from 0.0 to 1.0.
        """
        self._button_pressed(
            "Right_Trigger", self.xbox_controller.getRightTriggerAxis() >= 0.5
        )
        return self.xbox_controller.getRightTriggerAxis()

    def right_trigger_was_pressed(self) -> bool:
        """
        Check if the right trigger was pressed since the last check.

        :return: True if the right trigger was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Right_Trigger")

    def start_button_pressed(self) -> bool:
        """
        Check if the start button is pressed.

        :return: True if the start button is pressed, False otherwise.
        """
        return self._button_pressed("Start", self.xbox_controller.getStartButton())

    def start_button_was_pressed(self) -> bool:
        """
        Check if the start button was pressed since the last check.

        :return: True if the start button was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Start")

    def back_button_pressed(self) -> bool:
        """
        Check if the back button is pressed.

        :return: True if the back button is pressed, False otherwise.
        """
        return self._button_pressed("Back", self.xbox_controller.getBackButton())

    def back_button_was_pressed(self) -> bool:
        """
        Check if the back button was pressed since the last check.

        :return: True if the back button was pressed since the last check, False otherwise.
        """
        return self._button_was_pressed("Back")
