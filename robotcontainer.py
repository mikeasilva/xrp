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
        """
        # =====================================================================
        #   B BUTTON
        # =====================================================================
        self.joystick.getBButtonPressed().whenPressed(
            # B button pressed = fast mode
            #self.network_tables.max_speed.set(1.0)
        )
        
        self.joystick.getBButtonReleased().whenReleased(
            # Switch back to normal speed when released
            #self.network_tables.max_speed.set(constants.MAX_SPEED)
        )
        # =====================================================================

        # =====================================================================
        #   X BUTTON
        # =====================================================================

        # =====================================================================
        #   Y BUTTON
        # =====================================================================
        self.joystick.getYButtonPressed().whenPressed(
            # Disable crash avoidance when Y button is pressed
            self.drive.set_crash_avoidance_enabled(False)
        )
        self.joystick.getYButtonReleased().whenReleased(
            # Enable crash avoidance when Y button is released
            self.drive.set_crash_avoidance_enabled(True)
        )
        # =====================================================================
        #"""
