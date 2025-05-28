from components.motor import XRPMotor


class Drivetrain:
    def __init__(self, left_motor: XRPMotor, right_motor: XRPMotor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def enabled(self):
        self.stop()

    def execute(self):
        pass

    def set_speed(self, speed):
        self.left_motor.set_speed(speed)
        self.right_motor.set_speed(speed)

    def stop(self):
        self.set_speed(0)
