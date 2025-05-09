import commands
import commands2
import constants
import subsystems


class RobotContainer:
    def __init__(self):
        # Define the topics and their types for network tables
        # The topics and types are defined in the format (topic_name, topic_type)
        topics_and_types = [
            ("state", "string"),
            ("crash-avoidance-activated", "boolean"),
            ("max-speed", "double"),
            ("closest-object", "double"),
            ("x", "double"),
            ("y", "double"),
            ("z", "double"),
        ]

        # Initialize the subsystems
        self.arm = subsystems.Arm()
        self.controller = subsystems.Controller("Xbox")
        self.drive = subsystems.XRPDrive()
        self.led = subsystems.LED()
        self.network_tables = subsystems.NetworkTables("XRP", topics_and_types)
        self.network_tables.update("max-speed", constants.MAX_SPEED)
        # Configure the buttons
        self.configure_button_bindings()
        # Set the default command
        default_command = commands.TeleopDrive(
            self.drive, self.controller, self.network_tables
        )
        self.drive.setDefaultCommand(default_command)

    def configure_button_bindings(self):
        """Configure button bindings for the robot."""

        # =====================================================================
        #   A BUTTON
        # =====================================================================
        a_button = self.controller.a_button
        # A button pressed = Extend the arm
        a_button.onTrue(commands2.InstantCommand(lambda: self.arm.extend()))
        # A button released = Retract the arm
        a_button.onFalse(commands2.InstantCommand(lambda: self.arm.retract()))
        # =====================================================================

        # =====================================================================
        #   B BUTTON
        # =====================================================================
        b_button = self.controller.b_button
        # B button pressed = fast mode
        b_button.onTrue(
            commands2.InstantCommand(
                lambda: self.network_tables.update("max-speed", 1.0)
            )
        )
        # Switch back to normal speed when released
        b_button.onFalse(
            commands2.InstantCommand(
                lambda: self.network_tables.update("max-speed", constants.MAX_SPEED)
            )
        )
        # =====================================================================

        # =====================================================================
        #   X BUTTON
        # =====================================================================
        x_button = self.controller.x_button

        x_button.onTrue(commands.TurnTo(0, self.drive, self.network_tables))
        # =====================================================================

        # =====================================================================
        #   Y BUTTON
        # =====================================================================
        y_button = self.controller.y_button
        # Disable crash avoidance when Y button is pressed
        y_button.onTrue(
            commands2.InstantCommand(
                lambda: self.drive.set_crash_avoidance_enabled(False)
            )
        )
        # Enable crash avoidance when Y button is released
        y_button.onFalse(
            commands2.InstantCommand(
                lambda: self.drive.set_crash_avoidance_enabled(True)
            )
        )
        # =====================================================================

        # =====================================================================
        #   LEFT BUMPER
        # =====================================================================
        left_bumper = self.controller.left_bumper
        left_bumper.onTrue(commands.Turn(90, "CCW", self.drive, self.network_tables))
        # =====================================================================

        # =====================================================================
        #   RIGHT BUMPER
        # =====================================================================
        right_bumper = self.controller.right_bumper
        right_bumper.onTrue(commands.Turn(90, "CW", self.drive, self.network_tables))
        # =====================================================================

    def get_autonomous_command(self):
        # Drive forward for a bit
        return commands.AutonomousDrive(
            self.drive, duration=2.0, speed=self.network_tables.read("max-speed")
        )
