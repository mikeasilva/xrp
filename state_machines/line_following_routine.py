import components
import  magicbot.state_machine

class LineFollowingRoutine(magicbot.state_machine.StateMachine):
    drivetrain: components.DriveTrain
    reflectance_sensor: components.ReflectanceSensor

    TARGET_BRIGHTNESS = 0.5  # Desired brightness level for line following
    BASE_SPEED = 0.4         # Base speed of the robot
    P = 0.6                 # Proportional gain for correction

    @magicbot.state_machine.state(first=True)
    def follow_line(self):
        left_error = self.TARGET_BRIGHTNESS - self.reflectance_sensor.left_reflectance()
        right_error = self.TARGET_BRIGHTNESS - self.reflectance_sensor.right_reflectance()

        # Clamp speeds to valid range [-1, 1]
        left_speed = max(min((self.BASE_SPEED + (self.P * left_error)), 1), -1)
        right_speed = max(min((self.BASE_SPEED + (self.P * right_error)), 1), -1)

        self.drivetrain.drive.tankDrive(left_speed, right_speed)

    @magicbot.state_machine.state
    def stop(self):
        self.drivetrain.stop()

    @magicbot.state_machine.timed_state(duration=10, next_state='stop')
    def timed_follow(self):
        self.follow_line()