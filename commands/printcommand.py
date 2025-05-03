import commands2


class PrintCommand(commands2.Command):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def initialize(self):
        print(self.message)

    def isFinished(self):
        return True
