import magicbot
import components
import constants


class MyRobot(magicbot.MagicRobot):
    drivetrain: components.Drivetrain
    left_motor: components.XRPMotor
    right_motor: components.XRPMotor

    def createObjects(self):
        self.left_motor = components.XRPMotor(
            channel=constants.LEFT_MOTOR_CHANNEL, name="LeftMotor", inverted=False
        )
        self.right_motor = components.XRPMotor(
            channel=constants.RIGHT_MOTOR_CHANNEL, name="RightMotor", inverted=True
        )
        self.drivetrain = components.Drivetrain(self.left_motor, self.right_motor)

    def teleopPeriodic(self):
        # For this example, always move forward at 0.5 speed in teleop
        self.drivetrain.set_speed(0.5)
