import xrp


class XRPMotor:
    motor: xrp.XRPMotor
    speed: float
    name: str

    def __init__(self, channel: int, name: str, inverted: bool = False) -> None:
        self.motor = xrp.XRPMotor(channel)
        self.motor.setInverted(inverted)
        self.speed = 0.0
        self.name = name

    def set_speed(self, speed: float) -> None:
        if speed != self.speed:
            print(f"Setting speed of {self.name} to {speed}")
            self.speed = speed
            self.motor.set(self.speed)

    def enabled(self) -> None:
        self.set_speed(0)

    def execute(self) -> None:
        # pass
        self.motor.feed()
