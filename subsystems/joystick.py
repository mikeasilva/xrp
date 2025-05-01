import commands2
import constants
import wpilib
import json


class Joystick(commands2.Subsystem):
    def __init__(self) -> None:
        super().__init__()
        self.joystick = wpilib.Joystick(constants.CONTROLLER_PORT)

        # Read in the joystick drift
        try:
            with open("joystick_drift.json", "r") as f:
                self.joystick_drift = json.load(f)
        except:
            self.joystick_drift = {
                "left": 0.0,
                "right": 0.0,
            }

    def a_button_pressed(self) -> bool:
        return self.joystick.getRawButtonPressed(1)

    def get_dpad(self) -> int:
        """
        Get the D-pad value
        """
        return self.joystick.getPOV()

    def get_left_stick(self) -> float:
        """
        Get the left stick value
        """
        return (
            self.joystick.getRawAxis(constants.CONTROLLER_LEFT_STICK)
            + self.joystick_drift["left"]
        )

    def get_right_stick(self) -> float:
        """
        Get the right stick value
        """
        return (
            self.joystick.getRawAxis(constants.CONTROLLER_RIGHT_STICK)
            + self.joystick_drift["right"]
        )
