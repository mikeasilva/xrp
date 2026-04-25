from magicbot import MagicRobot, feedback

class MyRobot(MagicRobot):

    def createObjects(self):
        '''Create motors and stuff here'''
        pass

    def teleopInit(self):
        '''Called when teleop starts; optional'''
        pass

    def teleopPeriodic(self):
        pass

    @feedback(key="is")
    def get_current_state(self):
        '''Return the current state of the robot'''
        return "STARTING UP"