#!/usr/bin/env python3

import wpilib
import rev


class MyRobot(wpilib.TimedRobot):
    def robotInit(self) -> None:
        self.sol = wpilib.DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 6, 7)
        self.joystick = wpilib.Joystick(0)
        self.compressor = wpilib.Compressor(wpilib.PneumaticsModuleType.CTREPCM)

        self.intake_motor = rev.CANSparkMax(1, rev.CANSparkMax.MotorType.kBrushless)
        self.shooter_motor = rev.CANSparkMax(2, rev.CANSparkMax.MotorType.kBrushless)

    def teleopPeriodic(self) -> None:
        b1 = self.joystick.getRawButton(5)
        b2 = self.joystick.getRawButton(6)

        if b1:
            self.sol.set(wpilib.DoubleSolenoid.Value.kForward)
        elif b2:
            self.sol.set(wpilib.DoubleSolenoid.Value.kReverse)
        else:
            self.sol.set(wpilib.DoubleSolenoid.Value.kOff)

        self.intake_motor.set(self.joystick.getY())

        b3 = self.joystick.getRawButton(11)
        if b3:
            self.shooter_motor.set(self.joystick.getZ())
        else:
            self.shooter_motor.set(0)


if __name__ == "__main__":
    wpilib.run(MyRobot)
