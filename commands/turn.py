import commands2


class Turn(commands2.Command):
    def __init__(self, degrees:float, direction:str, turn_speed:float, initial_angle:float, drive):
        super().__init__()
        direction = direction.upper()
        if direction not in ["CW", "CCW"]:
            raise ValueError("Direction must be 'CW' or 'CCW'")
        self.direction = direction
        self.turn_speed = turn_speed
        self.current_angle = initial_angle
        self.target_angle = initial_angle + degrees if direction == "CW" else initial_angle - degrees
        self.drive = drive
        self.addRequirements(drive)

    def initialize(self):
        pass

    def execute(self):
        if self.direction == "CW":
            self.drive.tank_drive(self.turn_speed, -self.turn_speed)
        else:
            self.drive.tank_drive(-self.turn_speed, self.turn_speed)
        self.drive.periodic()
        self.current_angle = self.drive.get_gyro_angle()

    def isFinished(self):
        return self.current_angle == self.target_angle

    def end(self, interrupted):
        self.drive.stop()
