import components
import magicbot.state_machine


class DriveStraight(magicbot.state_machine.StateMachine):
    drivetrain: components.DriveTrain

    def start(self, target_distance, unit):
        print("Drive straight state machine - start")
        self.target_distance = target_distance
        self.unit = unit
        self.state_counter = 0
        self.engage()

    @magicbot.state_machine.state(first=True)
    def begin(self):
        print("Drive straight state machine - begin")
        # Configuration should run only on the first iteration of 'begin'
        if self.state_counter == 0:
            self.drivetrain.set_encoder_units(self.unit)
            self.drivetrain.reset_encoders()
            self.initial_heading = self.drivetrain.gyro.yaw()
            # Setpoints define the targets for the PID controllers
            self.drivetrain.set_distance_pid_setpoint(self.target_distance)
            self.drivetrain.set_heading_pid_setpoint(0)
            self.state_counter = 1

        # PID Calculation happens every loop iteration
        
        # 1. Calculate distance speed: How fast to move forward/backward
        #    (Assumes 'get_distance()' method exists in DriveTrain)
        current_distance = self.drivetrain.distance() 
        distance_output = self.drivetrain.distance_PID.calculate(current_distance)

        # 2. Calculate heading adjustment: How much to turn to stay straight
        current_heading = self.drivetrain.gyro.yaw()
        error = self.initial_heading - current_heading # Or use a heading PID controller calculate method
        adjustment = self.drivetrain.heading_PID.calculate(error)

        # 3. Combine PIDs into left/right motor speeds
        left_speed = distance_output + adjustment
        right_speed = distance_output - adjustment

        print(f"SPEEDS - Left: {left_speed}; Right: {right_speed}")

        # 4. Command the drivetrain (sets internal variables, execute() applies them)
        #    Assumes 'set_speeds(left, right)' method exists in DriveTrain
        self.drivetrain.tank_drive(left_speed, right_speed)

        # 5. Check termination condition
        #    Note: Tuning PIDs so they simultaneously hit setpoint is hard. 
        #    Often you check if *one* is done.
        if self.drivetrain.distance_PID.atSetpoint(): # AND self.drivetrain.heading_PID.atSetpoint()
            self.next_state("finish")

    @magicbot.state()
    def finish(self):
        print("Drive straight state machine - finish")
        self.drivetrain.stop()
        self.done()
