import magicbot
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A21

from subsystems.indicator import Indicator


class BarDetect:

    left_bar_sensor: SharpIR2Y0A21
    right_bar_sensor: SharpIR2Y0A21

    indicator: Indicator

    detect_enabled = magicbot.will_reset_to(False)
    detect_debug = magicbot.tunable(False)

    def enable_detector(self):
        self.detect_enabled = True

    @magicbot.feedback
    def left_distance(self):
        return self.left_bar_sensor.getDistance()

    @magicbot.feedback
    def right_distance(self):
        return self.right_bar_sensor.getDistance()

    def execute(self):
        if self.detect_enabled or self.detect_debug:
            ld = self.left_distance()
            rd = self.right_distance()

            l = False
            r = False

            # low bar is ~20 cm, high bar is ~50cm
            if ld > 15 and ld < 55:
                l = True

            if rd > 15 and rd < 55:
                r = True

            self.indicator.set_bar_sensing(l, r)
