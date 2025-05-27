import magicbot
import components


class Robot(magicbot.MagicRobot):
    led: components.LED

    def createObjects(self):
        """Create motors and stuff here"""
        pass

    def teleopInit(self):
        """Called when teleop starts; optional"""
        pass

    def teleopPeriodic(self):
        """Called every 20ms during teleop"""
        # Blink the LED to indicate mode
        self.led.blink()
