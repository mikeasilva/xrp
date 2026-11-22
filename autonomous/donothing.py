from magicbot import AutonomousStateMachine, timed_state


class DoNothing(AutonomousStateMachine):
    MODE_NAME = "Do Nothing"
    DEFAULT = True

    @timed_state(duration=3, first=True)
    def do_nothing(self):
        pass
