import commands2
import wpilib


class AutonomousDrive(commands2.Command):
    def __init__(self, drive, duration, speed):
        super().__init__()
        self.drive = drive
        self.duration = duration
        self.speed = speed
        self.timer = wpilib.Timer()
        self.addRequirements(drive)

    def initialize(self):
        self.timer.reset()
        self.timer.start()

    def execute(self):
        self.drive.tank_drive(self.speed, self.speed)

    def isFinished(self):
        return self.timer.hasElapsed(self.duration)

    def end(self, interrupted):
        self.drive.stop()
