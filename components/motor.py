import xrp


class XRPMotor:
    motor = xrp.XRPMotor

    def __init__(self, channel: int, name:str, inverted: bool = False):
        self.motor = xrp.XRPMotor(channel)
        self.motor.setInverted(inverted)
        self.speed = 0.0
        self.name = name

    def set_speed(self, speed: float):
        if speed != self.speed:
            # Only print if the speed is actually changing
            print(f"Setting speed of {self.name} to {speed}")
            self.speed = speed
            self.motor.set(self.speed)
            self.motor.feed()

    def execute(self):
        pass
