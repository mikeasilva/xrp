import magicbot
import qwiic_huskylens
import qwiic_i2c
import wpilib

class HuskyLens:
    default_algorithm: str
    address = 0x32  # default HuskyLens I2C address

    def execute(self) -> None:
        pass

    def setup(self) -> None:
        driver = qwiic_i2c.get_i2c_driver()
        self.husky_lens = qwiic_huskylens.QwiicHuskylens(i2c_driver=driver, address=self.address)
        if not self.husky_lens.connected:
            print("ERROR: HuskyLens not detected on Qwiic!")
        else:
            print("HuskyLens connected!")
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
