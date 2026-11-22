"""A simple Xbox controller helper for MagicBot.

This component wraps a real Xbox controller and makes it easier to use in
robot code. It remembers when a button was just pressed so your code can react
once instead of every loop. In a RobotPy MagicBot project, declare the
component and set its controller port in ``createObjects``::

    from components.xboxcontroller import XboxController
    from magicbot import MagicRobot

    class Robot(MagicRobot):
        controller: XboxController

        def createObjects(self):
            self.controller = XboxController()
            self.controller.port = 0

        def teleopPeriodic(self):
            forward = -self.controller.left_y
            turn = self.controller.right_x

            if self.controller.a_button_was_pressed():
                print("A was pressed!")

MagicBot creates and runs the component for you. Read values such as
``left_x``, ``left_y``, ``right_x``, and ``right_y`` in your robot code, and
call ``execute()`` once each control loop to update the current controller
state. The component also provides methods like ``a_button_pressed()`` and
``a_button_was_pressed()`` for checking buttons. Use the "was pressed" version
for actions that should happen only once, like turning a feature on or off.

Set ``port`` to the controller's USB port number. Joystick values are exposed
as the raw axis readings from -1.0 to 1.0. Apply deadband, response curves,
and acceleration limiting in the drivetrain.
"""

import wpilib


class XboxController:
    """Helper for reading Xbox controller state in a MagicBot component.

    This wrapper exposes raw joystick values and tracks button press
    transitions that are useful for robot control logic.
    """

    port: int
    left_x: float = 0.0
    left_y: float = 0.0
    right_x: float = 0.0
    right_y: float = 0.0

    def setup(self) -> None:
        """Set up the Xbox controller.

        This method is called once when the robot is initialized.
        """
        self.this_controller = wpilib.XboxController(self.port)
        controller_buttons = [
            "A",
            "B",
            "X",
            "Y",
            "DPad_Up",
            "DPad_Down",
            "DPad_Left",
            "DPad_Right",
            "Left_Bumper",
            "Right_Bumper",
            "Left_Trigger",
            "Right_Trigger",
            "Start",
            "Back",
        ]
        self.button_is_pressed = {button: False for button in controller_buttons}
        self.button_was_pressed = {button: False for button in controller_buttons}

    def _button_pressed(self, button_name: str, pressed: bool) -> bool:
        """Check if a button is pressed.

        :param button_name: The name of the button to check.
        :param pressed: The current state of the button (True if pressed, False if not).
        """
        if self.button_is_pressed[button_name] and not pressed:
            self.button_was_pressed[button_name] = True
        self.button_is_pressed[button_name] = pressed
        return pressed

    def _button_was_pressed(self, button_name: str) -> bool:
        """Check if a button was pressed since the last check.

        :param button_name: The name of the button to check.
        :return: True if the button was pressed since the last check, False if not
        """
        if self.button_was_pressed[button_name]:
            self.button_was_pressed[button_name] = False
            return True
        return False

    def execute(self) -> None:
        """Capture the current state of all buttons to track presses.

        This method should be called at the end of each control loop iteration.
        """
        self.a_button_pressed()
        self.b_button_pressed()
        self.x_button_pressed()
        self.y_button_pressed()
        self.dpad_up_pressed()
        self.dpad_down_pressed()
        self.dpad_left_pressed()
        self.dpad_right_pressed()
        self.left_bumper_pressed()
        self.right_bumper_pressed()
        self.left_trigger_pressed()
        self.right_trigger_pressed()
        self.start_button_pressed()
        self.back_button_pressed()
        self.left_x = self.this_controller.get_left_x()
        self.left_y = self.this_controller.get_left_y()
        self.right_x = self.this_controller.get_right_x()
        self.right_y = self.this_controller.get_right_y()

    def a_button_pressed(self) -> bool:
        """Check if the A button is pressed.

        :return: True if the A button is pressed, False if not
        """
        return self._button_pressed("A", self.this_controller.get_a_button())

    def a_button_was_pressed(self) -> bool:
        """Check if the A button was pressed since the last check.

        :return: True if the A button was pressed since the last check, False if not
        """
        return self._button_was_pressed("A")

    def b_button_pressed(self) -> bool:
        """Check if the B button is pressed.

        :return: True if the B button is pressed, False if not
        """
        return self._button_pressed("B", self.this_controller.get_b_button())

    def b_button_was_pressed(self) -> bool:
        """Check if the B button was pressed since the last check.

        :return: True if the B button was pressed since the last check, False if not
        """
        return self._button_was_pressed("B")

    def x_button_pressed(self) -> bool:
        """Check if the X button is pressed.

        :return: True if the X button is pressed, False if not
        """
        return self._button_pressed("X", self.this_controller.get_x_button())

    def x_button_was_pressed(self) -> bool:
        """Check if the X button was pressed since the last check.

        :return: True if the X button was pressed since the last check, False if not
        """
        return self._button_was_pressed("X")

    def y_button_pressed(self) -> bool:
        """Check if the Y button is pressed.

        :return: True if the Y button is pressed, False if not
        """
        return self._button_pressed("Y", self.this_controller.get_y_button())

    def y_button_was_pressed(self) -> bool:
        """Check if the Y button was pressed since the last check.

        :return: True if the Y button was pressed since the last check, False if not
        """
        return self._button_was_pressed("Y")

    def dpad_up_pressed(self) -> bool:
        """Check if the D-pad is pressed up.

        :return: True if the D-pad is pressed up, False if not
        """
        return self._button_pressed(
            "DPad_Up", self.this_controller.get_dpad_up_button()
        )

    def dpad_up_was_pressed(self) -> bool:
        """Check if the D-pad was pressed up since the last check.

        :return: True if the D-pad up was pressed since the last check, False if not
        """
        return self._button_was_pressed("DPad_Up")

    def dpad_down_pressed(self) -> bool:
        """Check if the D-pad is pressed down.

        :return: True if the D-pad is pressed down, False if not
        """
        return self._button_pressed(
            "DPad_Down", self.this_controller.get_dpad_down_button()
        )

    def dpad_down_was_pressed(self) -> bool:
        """Check if the D-pad was pressed down since the last check.

        :return: True if D-pad down was pressed since the last check, False if not
        """
        return self._button_was_pressed("DPad_Down")

    def dpad_left_pressed(self) -> bool:
        """Check if the D-pad is pressed left.

        :return: True if the D-pad is pressed left, False if not
        """
        return self._button_pressed(
            "DPad_Left", self.this_controller.get_dpad_left_button()
        )

    def dpad_left_was_pressed(self) -> bool:
        """Check if the D-pad was pressed left since the last check.

        :return: True if the D-pad left pressed since the last check, False if not
        """
        return self._button_was_pressed("DPad_Left")

    def dpad_right_pressed(self) -> bool:
        """Check if the D-pad is pressed right.

        :return: True if the D-pad is pressed right, False if not
        """
        return self._button_pressed(
            "DPad_Right", self.this_controller.get_dpad_right_button()
        )

    def dpad_right_was_pressed(self) -> bool:
        """Check if the D-pad was pressed right since the last check.

        :return: True if D-pad right pressed since the last check, False if not
        """
        return self._button_was_pressed("DPad_Right")

    def left_bumper_pressed(self) -> bool:
        """Check if the left bumper is pressed.

        :return: True if the left bumper is pressed, False if not
        """
        return self._button_pressed(
            "Left_Bumper", self.this_controller.get_left_bumper_button()
        )

    def left_bumper_was_pressed(self) -> bool:
        """Check if the left bumper was pressed since the last check.

        :return: True if the left bumper pressed since the last check, False if not
        """
        return self._button_was_pressed("Left_Bumper")

    def right_bumper_pressed(self) -> bool:
        """Check if the right bumper is pressed.

        :return: True if the right bumper is pressed, False if not
        """
        return self._button_pressed(
            "Right_Bumper", self.this_controller.get_right_bumper_button()
        )

    def right_bumper_was_pressed(self) -> bool:
        """Check if the right bumper was pressed since the last check.

        :return: True if the right bumper pressed since the last check, False if not
        """
        return self._button_was_pressed("Right_Bumper")

    def left_trigger_pressed(self) -> float:
        """Get the value of the left trigger.

        :return: The value of the left trigger, ranging from 0.0 to 1.0.
        """
        self._button_pressed(
            "Left_Trigger", self.this_controller.get_left_trigger() >= 0.5
        )
        return self.this_controller.get_left_trigger()

    def left_trigger_was_pressed(self) -> bool:
        """Check if the left trigger was pressed since the last check.

        :return: True if the left trigger pressed since the last check, False if not
        """
        return self._button_was_pressed("Left_Trigger")

    def right_trigger_pressed(self) -> float:
        """Get the value of the right trigger.

        :return: The value of the right trigger, ranging from 0.0 to 1.0.
        """
        self._button_pressed(
            "Right_Trigger", self.this_controller.get_right_trigger() >= 0.5
        )
        return self.this_controller.get_right_trigger()

    def right_trigger_was_pressed(self) -> bool:
        """Check if the right trigger was pressed since the last check.

        :return: True if the right trigger pressed since the last check, False if not
        """
        return self._button_was_pressed("Right_Trigger")

    def start_button_pressed(self) -> bool:
        """Check if the start button is pressed.

        :return: True if the start button is pressed, False if not
        """
        return self._button_pressed("Start", self.this_controller.get_menu_button())

    def start_button_was_pressed(self) -> bool:
        """Check if the start button was pressed since the last check.

        :return: True if the start button pressed since the last check, False if not
        """
        return self._button_was_pressed("Start")

    def back_button_pressed(self) -> bool:
        """Check if the back button is pressed.

        :return: True if the back button is pressed, False if not
        """
        return self._button_pressed("Back", self.this_controller.get_view_button())

    def back_button_was_pressed(self) -> bool:
        """Check if the back button was pressed since the last check.

        :return: True if the back button pressed since the last check, False if not
        """
        return self._button_was_pressed("Back")
