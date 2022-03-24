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
    turningSpeed = magicbot.tunable(0.2)

    # all of these are in cm
    sensor_height = 74
    bar1_height = 124 - sensor_height
    bar2_height = 153 - sensor_height

    height_error = magicbot.tunable(5)

    def setup(self):
        self.specialMode = False
        self.bar_height_min = 0
        self.bar_height_max = 0

    def enableAssistLow(self):
        self.assist_enabled = True
        self.bar_height_min = self.bar1_height - self.height_error
        self.bar_height_max = self.bar1_height + self.height_error

    def enableAssistMid(self):
        self.assist_enabled = True
        self.bar_height_min = self.bar2_height - self.height_error
        self.bar_height_max = self.bar2_height + self.height_error

    @magicbot.feedback
    def left_distance(self):
        return self.left_bar_sensor.getDistance()

    @magicbot.feedback
    def right_distance(self):
        return self.right_bar_sensor.getDistance()

    def underL(self):
        """this will return true if the left sensor is under the selected bar"""
        d = self.left_bar_sensor.getDistance()
        return d < self.bar_height_max and d > self.bar_height_min

    def underR(self):
        """this will return true if the right sensor is under the selected bar"""
        d = self.right_bar_sensor.getDistance()
        return d < self.bar_height_max and d > self.bar_height_min

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
