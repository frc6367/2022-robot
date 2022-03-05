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

    def enableAssist(self):
        self.assist_enabled = True

    def execute(self):
        if not self.assist_enabled:
            return

        # implement flow chart here
