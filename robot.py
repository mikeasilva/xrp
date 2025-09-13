import components
import magicbot

class MyRobot(magicbot.MagicRobot):
    drivetrain: components.DriveTrain

    def createObjects(self):
        '''Create motors and stuff here'''
        pass

    def teleopInit(self):
        '''Called when teleop starts; optional'''
        pass

    def teleopPeriodic(self):
        pass