from subsystems.climber import Climber
from subsystems.drivetrain import DriveTrain

import magicbot
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A21


class ClimbAssistant:
    """
    The ClimbAssistant is supposed to make it easier for the driver
    to align the robot to the climbing bar.
    """

    climber: Climber
    drivetrain: DriveTrain

    left_bar_sensor: SharpIR2Y0A21
    right_bar_sensor: SharpIR2Y0A21

    assist_enabled = magicbot.will_reset_to(False)
    specialMode = False

    def enableAssist(self):
        self.assist_enabled = True

    def underL(self):
        """this will return true if the left sensor is under the bar"""

    def underR(self):
        """this will return true if the right sensor is under the bar"""

    def execute(self):
        if not self.assist_enabled:
            self.specialMode = False
        if self.assist_enabled:
            self.specialMode = True
            if self.underL == True:
                if self.underR == True:
                    return
                if self.underR == False:
                    self.assist_enabled = True
            if self.underL == False:
                if self.underR == True:
                    self.assist_enabled = True
                if self.underR == False:
                    return

        # implement flow chart here
        # If the button is pressed, then it moves to the location
        # if it under L, tun counterclock wise for the right, opposite for the right.
        # if it not under, continue moving or staying, if it both under at the same time, stop the code.
