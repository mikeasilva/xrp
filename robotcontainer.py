import commands
import commands2
import constants
import subsystems
import wpilib


class RobotContainer:
    def __init__(self):
        # Define the topics and their types for network tables
        # The topics and types are defined in the format (topic_name, topic_type)
        topics_and_types = [
            ("state", "string"),
            ("crash-avoidance-activated", "boolean"),
            ("max-speed", "double"),
            ("x", "double"),
            ("y", "double"),
            ("z", "double"),
        ]

        # Initialize the subsystems
        self.drive = subsystems.Drive()
        self.led = subsystems.LED()
        self.joystick = wpilib.XboxController(constants.CONTROLLER_PORT)
        self.network_tables = subsystems.NetworkTables("XRP", topics_and_types)
        self.network_tables.update("max-speed", constants.MAX_SPEED)
        self.configure_button_bindings()
        # self.drive.setDefaultCommand(...)

    def get_autonomous_command(self):
        # Drive forward for a bit
        return commands.AutonomousDrive(
            self.drive, duration=2.0, speed=constants.MAX_SPEED
        )  # speed=self.network_tables.read('max-speed'))

    def get_teleop_command(self):
        return commands.TeleopDrive(self.drive, self.joystick, self.network_tables)

    def configure_button_bindings(self):
        """Configure button bindings for the robot."""

        # =====================================================================
        #   A BUTTON
        # =====================================================================
        a_button = commands2.button.JoystickButton(
            self.joystick, wpilib.XboxController.Button.kA
        )
        a_button.onTrue(commands.PrintCommand("A Pressed"))
        a_button.onFalse(commands.PrintCommand("A Released"))

        # =====================================================================
        #   B BUTTON
        # =====================================================================
        b_button = commands2.button.JoystickButton(
            self.joystick, wpilib.XboxController.Button.kB
        )
        # B button pressed = fast mode
        b_button.onTrue(commands2.InstantCommand(lambda: self.network_tables.update("max-speed", 1.0)))
        # Switch back to normal speed when released
        b_button.onFalse(commands2.InstantCommand(lambda: self.network_tables.update("max-speed", constants.MAX_SPEED)))
        # =====================================================================
        
        # =====================================================================
        #   X BUTTON
        # =====================================================================

        # =====================================================================
        #   Y BUTTON
        # =====================================================================
        y_button = commands2.button.JoystickButton(
            self.joystick, wpilib.XboxController.Button.kY
        )
        # Disable crash avoidance when Y button is pressed
        y_button.onTrue(commands2.InstantCommand(lambda: self.drive.set_crash_avoidance_enabled(False)))
        # Enable crash avoidance when Y button is released
        y_button.onFalse(commands2.InstantCommand(lambda: self.drive.set_crash_avoidance_enabled(True)))
        # =====================================================================
