import components
import magicbot.state_machine


class LineFollowingRoutine(magicbot.state_machine.StateMachine):
    drivetrain: components.DriveTrain
    reflectance_sensor: components.ReflectanceSensor

    TARGET_BRIGHTNESS = 0.5  # Desired brightness level for line following
    BASE_SPEED = 0.4  # Base speed of the robot
    P = 0.6  # Proportional gain for correction
    I = 0.0  # Integral gain (not used in this simple example)
    D = 0.0  # Derivative gain (not used in this simple example)

    @magicbot.state_machine.state(first=True)
    def initialize(self):
        if self.reflectance_sensor.senses_a_line():
            self.next_state("follow_the_line")
        else:
            self.next_state("find_the_line")

    @magicbot.state_machine.state()
    def find_the_line(self):
        while True:
            # Drive forward searching for the line
            self.drivetrain.drive.arcadeDrive(self.BASE_SPEED, 0)
            if self.reflectance_sensor.senses_a_line():
                self.next_state("follow_line")

    @magicbot.state_machine.state(first=True)
    def follow_the_line(self):
        left_error = self.TARGET_BRIGHTNESS - self.reflectance_sensor.left_reflectance()
        right_error = (
            self.TARGET_BRIGHTNESS - self.reflectance_sensor.right_reflectance()
        )

        # Clamp speeds to valid range [-1, 1]
        left_speed = max(min((self.BASE_SPEED + (self.P * left_error)), 1), -1)
        right_speed = max(min((self.BASE_SPEED + (self.P * right_error)), 1), -1)

        self.drivetrain.drive.tankDrive(left_speed, right_speed)

    @magicbot.state_machine.state
    def stop(self):
        self.drivetrain.stop()

    @magicbot.state_machine.timed_state(duration=10, next_state="stop")
    def timed_follow(self):
        self.follow_the_line()
