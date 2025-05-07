import commands2


class PrintMe(commands2.Command):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def initialize(self) -> None:
        print(self.message)

    def isFinished(self) -> bool:
        return True
