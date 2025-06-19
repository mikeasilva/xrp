import components
import magicbot
import random
import wpilib

class RandomWalk(magicbot.AutonomousStateMachine):
    MODE_NAME = "Random Walk"
    DEFAULT = False

    arm: components.Arm
    drivetrain: components.Drivetrain
    odometry: components.Odometry
    led: components.LED
    forward_speed = 0.0
    forward_sign = 1
    turn_speed = 0.0
    steps = magicbot.tunable(0)
    time_for_step = 1.0
    initial_x = magicbot.tunable(0.0)
    initial_y = magicbot.tunable(0.0)
    end_x = magicbot.tunable(100.0)
    end_y = magicbot.tunable(100.0)

    @magicbot.state(first=True)
    def record_location(self):
        self.led.on()
        self.arm.retract()
        self.timer = wpilib.Timer()
        self.steps = random.randint(5, 10)
        location = self.odometry.get_location()
        self.initial_x = location.x
        self.initial_y = location.y
        self.next_state("randomize")

    @magicbot.state()
    def randomize(self):        
        self.forward_speed = random.uniform(0.8, 1.0)
        self.forward_sign = 1 if random.random() > 0.5 else -1
        self.turn_speed = random.uniform(-1.0, 1.0)
        self.time_for_step = random.uniform(2.0, 5.0)   
        if self.steps == 0:
            self.next_state("record_end_location")
        else:
            self.steps -= 1     
            self.next_state("start_walk")

    @magicbot.state()
    def start_walk(self):
        self.timer.reset()
        self.timer.start()
        while self.timer.get() < self.time_for_step:
            self.drivetrain.go(self.forward_sign * self.forward_speed, 0)
        self.time_for_step = random.uniform(2.0, 3.0)
        self.timer.reset()
        self.timer.start()
        self.next_state("turn")

    @magicbot.state()
    def turn(self):
        while self.timer.get() < self.time_for_step:
           self.drivetrain.go(0, self.turn_speed)
        self.next_state("randomize")

    @magicbot.state()
    def record_end_location(self):
        self.led.on()
        self.timer.stop()
        location = self.odometry.get_location()
        self.end_x = location.x
        self.end_y = location.y
        self.next_state("stop")

    @magicbot.state()
    def stop(self):
        self.led.off()
        self.drivetrain.stop()
        self.done()
