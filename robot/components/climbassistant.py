from subsystems.climber import Climber
from subsystems.drivetrain import DriveTrain

import magicbot
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A02


class ClimbAssistant:
    """
    The ClimbAssistant is supposed to make it easier for the driver
    to align the robot to the climbing bar.
    """

    climber: Climber
    drivetrain: DriveTrain

    left_bar_sensor: SharpIR2Y0A02
    right_bar_sensor: SharpIR2Y0A02

    assist_enabled = magicbot.will_reset_to(False)
    specialMode = False
    turningSpeed = magicbot.tunable(0.3)

    def enableAssist(self):
        self.assist_enabled = True

    @magicbot.feedback
    def left_distance(self):
        return self.left_bar_sensor.getDistance()

    @magicbot.feedback
    def right_distance(self):
        return self.left_bar_sensor.getDistance()

    def underL(self):
        """this will return true if the left sensor is under the bar"""

    def underR(self):
        """this will return true if the right sensor is under the bar"""

    def execute(self):
        if not self.assist_enabled:
            self.specialMode = False
        else:
            left = -self.turningSpeed
            right = self.turningSpeed
            underL = self.underL()
            underR = self.underR()

            if underL or underR:
                self.specialMode = True

            if self.specialMode:
                if underL:
                    if underR:
                        self.drivetrain.move(0, 0)
                        self.climber.raise_hook()
                    else:
                        self.drivetrain.rotate(left)
                else:
                    if underR:
                        self.drivetrain.rotate(right)
                    else:
                        self.drivetrain.rotate(0)

        # implement flow chart here
        # If the button is pressed, then it moves to the location
        # if it under L, tun counterclock wise for the right, opposite for the right.
        # if it not under, continue moving or staying, if it both under at the same time, stop the code.
