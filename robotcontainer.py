# from commands import *
import commands
import constants

# from subsystems import *
import subsystems
import wpilib


class RobotContainer:
    def __init__(self):
        self.drive = subsystems.Drive()
        self.led = subsystems.LED()
        self.joystick = wpilib.XboxController(constants.CONTROLLER_PORT)
        self.network_tables = subsystems.NetworkTables()
        self.network_tables.max_speed.set(constants.MAX_SPEED)
        # No joystick, so default command may not be needed.
        # self.drive.setDefaultCommand(...)

    def getAutonomousCommand(self):
        # Drive forward for a bit
        return commands.AutonomousDrive(self.drive, duration=2.0, speed=constants.MAX_SPEED)# speed=self.network_tables.get('max-speed'))

    def configureButtonBindings(self):
        """Configure button bindings for the robot."""

        # =====================================================================
        #   A BUTTON
        # =====================================================================
        self.joystick.getAButtonPressed().whenPressed(
            print("A")
        )
        # =====================================================================
        #   B BUTTON
        # =====================================================================
        self.joystick.getBButtonPressed().whenPressed(
            # B button pressed = fast mode
            self.network_tables.max_speed.set(1.0)
        )
        
        self.joystick.getBButtonReleased().whenReleased(
            # Switch back to normal speed when released
            self.network_tables.max_speed.set(constants.MAX_SPEED)
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


        