import wpilib
import magicbot
import xrp


class LED:
    io: xrp.XRPOnBoardIO
    blink_on_off_duration = magicbot.tunable(1.0)

    def __init__(self):
        # self.io = xrp.XRPOnBoardIO()
        self.enabled = False
        self.io.setLed(self.enabled)
        self.blink_timer = wpilib.Timer()

    def blink(self) -> None:
        """
        Blink the LED for a specified duration.
        """
        self.blink_timer.start()

        # How much time has passed?
        time = self.blink_timer.get()
        if time >= self.blink_on_off_duration:
            # If the LED is on, turn it off and vice versa
            if self.enabled:
                self.off()
            else:
                self.on()
            # Reset the timer
            self.blink_timer.reset()

    def off(self) -> None:
        """
        Turn the LED off.
        """
        self.enabled = False
        self.io.setLed(self.enabled)

    def on(self) -> None:
        """
        Turn the LED on.
        """
        self.enabled = True
        self.io.setLed(self.enabled)

    '''
    def enable(self):
        self.enabled = True

    def is_ready(self):
        # in a real robot, you'd be using an encoder to determine if the
        # shooter were at the right speed..
        return True

    def execute(self):
        """This gets called at the end of the control loop"""
        if self.enabled:
            self.shooter_motor.set(self.shoot_speed)
        else:
            self.shooter_motor.set(0)

        self.enabled = False
    '''
