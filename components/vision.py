import magicbot
import qwiic_huskylens


class HuskyLens:
    default_algorithm: str

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        self.husky_lens = qwiic_huskylens.QwiicHuskylens()
        if self.husky_lens.is_connected() == False:
            raise Exception("HuskyLens not connected. Please check your connection.")
        if self.husky_lens.begin() == False:
            raise Exception(
                "Failed to initialize the HuskyLens device. Please check your connection."
            )
        self.set_algorithm(self.default_algorithm)

    # =========================================================================
    # CONTROL METHODS
    # =========================================================================

    def set_algorithm(self, algorithm: str) -> None:
        algorithms = {
            "tag recognition": self.husky_lens.kAlgorithmTagRecognition,
            "object tracking": self.husky_lens.kAlgorithmObjectTracking,
            "face recognition": self.husky_lens.kAlgorithmFaceRecognition,
            "line tracking": self.husky_lens.kAlgorithmLineTracking,
            "color recognition": self.husky_lens.kAlgorithmColorRecognition,
        }
        self.current_algorithm = algorithm.lower()
        self.husky_lens.set_algorithm(algorithms[self.current_algorithm])

    # =========================================================================
    # INFORMATIONAL METHODS
    # =========================================================================

    def lines(self) -> list:
        self.set_algorithm("line tracking")
        return self.husky_lens.get_lines_of_interest()

    def objects(self) -> list:
        return self.husky_lens.get_objects_of_interest()

    @magicbot.feedback(key="Sees Things")
    def sees_things(self) -> bool:
        if self.current_algorithm == "line tracking":
            things = self.husky_lens.get_lines_of_interest()
        else:
            things = self.husky_lens.get_objects_of_interest()
        return len(things) > 0
