import components
import magicbot
import random


class RoombaMode(magicbot.AutonomousStateMachine):
    MODE_NAME = "Roomba"
    DEFAULT = True

    distance_sensor: components.DistanceSensor
    drivetrain: components.Drivetrain
    led: components.LED
    speed = 0.5
    turn_threshold = 6.0

    @magicbot.state(first=True)
    def forward(self):
        self.led.on()
        self.distance_sensor.execute()
        distance = self.distance_sensor.get_distance()
        if distance <= self.turn_threshold:
            self.next_state("turn")
        else:
            self.drivetrain.go(self.speed, 0)

    @magicbot.timed_state(duration=2.0, next_state="forward", must_finish=True)
    def turn(self):
        sign = 1 if random.random() > 0.5 else -1
        self.drivetrain.go(0, self.speed)

    @magicbot.state()
    def stop(self):
        self.led.off()
        self.drivetrain.stop()
        self.done()
