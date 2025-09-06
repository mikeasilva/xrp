from magicbot import tunable, feedback
from wpimath.controller import PIDController
import components

class TurnRight:
    drivetrain: components.Drivetrain

    kp = tunable(0.001)
    ki = tunable(0)
    kd = tunable(0)

    def setup(self):
        self.pid = PIDController(self.kp, self.ki, self.kd)
        self.pid.setTolerance(2.0)  # degrees
        self.target_angle = 0
        self.is_executing = False

    def engage(self):
        self.target_angle = 90#self.get_current_angle() + 90
        self.pid.setSetpoint(self.target_angle)
        self.is_executing = True

    def execute(self):
        if not self.is_executing:
            return
        
        if self.pid.atSetpoint():
            self.disable()
            return
        
        self.drivetrain.go(0, self.get_pid_output())

        

    def disable(self):
        self.is_executing = False
        self.pid.reset()

    @feedback(key="PID Output")
    def get_pid_output(self) -> float:
        return self.pid.calculate(self.get_current_angle())
    
    @feedback(key="Target Angle")
    def get_target_angle(self) -> float:
        return self.target_angle
    
    @feedback(key="Current Angle")
    def get_current_angle(self) -> float:
        return self.drivetrain.get_heading()
