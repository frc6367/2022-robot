#!/usr/bin/env python3

import wpilib


class MyRobot(wpilib.TimedRobot):
    def robotInit(self) -> None:
        self.sol = wpilib.DoubleSolenoid(6, 7)
        self.joystick = wpilib.Joystick(0)
        self.compressor = wpilib.Compressor()

    def teleopPeriodic(self) -> None:
        b1 = self.joystick.getRawButton(5)
        b2 = self.joystick.getRawButton(6)

        if b1:
            self.sol.set(wpilib.DoubleSolenoid.Value.kForward)
        elif b2:
            self.sol.set(wpilib.DoubleSolenoid.Value.kReverse)
        else:
            self.sol.set(wpilib.DoubleSolenoid.Value.kOff)


if __name__ == "__main__":
    wpilib.run(MyRobot)
