import components
import magicbot.state_machine


class AutoPilot(magicbot.state_machine.StateMachine):
    drivetrain: components.DriveTrain

    routines: dict

    @magicbot.state_machine.state(first=True)
    def load_routine(self):
        pass
