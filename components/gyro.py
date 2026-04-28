import magicbot
import wpimath.units
import xrp


class XRPGyro:
    def setup(self):
        self._gyro = xrp.XRPGyro()

    def execute(self):
        pass

    def reset(self):
        self._gyro.reset()

    @magicbot.feedback
    def angle(self) -> wpimath.units.radians:
        return self._gyro.getAngle()

    @magicbot.feedback
    def rotation(self) -> wpimath.units.degrees:
        return self._gyro.getRotation2d().degrees()
