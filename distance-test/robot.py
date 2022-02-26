#!/usr/bin/env python3

import wpilib
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A21


class MyRobot(wpilib.TimedRobot):
    def robotInit(self) -> None:
        self.DistSensor = SharpIR2Y0A21(0)

    def robotPeriodic(self) -> None:
        wpilib.SmartDashboard.putNumber("distance", self.DistSensor.getDistance())


if __name__ == "__main__":
    wpilib.run(MyRobot)
