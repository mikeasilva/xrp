from magicbot import AutonomousStateMachine, timed_state, state


class DoNothing(AutonomousStateMachine):
    MODE_NAME = "Do Nothing"
    DEFAULT = False

    @timed_state(duration=1, first=True, next_state="finish")
    def doing_nothing(self):
        pass

    @state()
    def finish(self):
        self.done()
