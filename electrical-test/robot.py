#!/usr/bin/env python3

import wpilib
import rev
import ctre

from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A21, SharpIR2Y0A41


class MyRobot(wpilib.TimedRobot):
    def robotInit(self) -> None:
        self.sol = wpilib.DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 6, 7)
        self.joystick = wpilib.Joystick(0)
        self.compressor = wpilib.Compressor(wpilib.PneumaticsModuleType.CTREPCM)

        self.belt_motor = rev.CANSparkMax(1, rev.CANSparkMax.MotorType.kBrushless)
        self.shooter_motor = rev.CANSparkMax(2, rev.CANSparkMax.MotorType.kBrushless)
        self.intake_motor = ctre.WPI_TalonSRX(7)

        self.d0 = SharpIR2Y0A41(0)
        self.d1 = SharpIR2Y0A41(1)
        self.d2 = SharpIR2Y0A21(2)
        self.d3 = SharpIR2Y0A21(3)

    def teleopPeriodic(self) -> None:
        b1 = self.joystick.getRawButton(5)
        b2 = self.joystick.getRawButton(6)

        if b1:
            self.sol.set(wpilib.DoubleSolenoid.Value.kForward)
        elif b2:
            self.sol.set(wpilib.DoubleSolenoid.Value.kReverse)
        else:
            self.sol.set(wpilib.DoubleSolenoid.Value.kOff)

        self.belt_motor.set(self.joystick.getY())

        b3 = self.joystick.getRawButton(11)
        if b3:
            self.intake_motor.set(self.joystick.getZ())
        else:
            self.intake_motor.set(0)

        wpilib.SmartDashboard.putNumber("A0-cm", self.d0.getDistance())
        wpilib.SmartDashboard.putNumber("A1-cm", self.d1.getDistance())
        wpilib.SmartDashboard.putNumber("A2-cm", self.d2.getDistance())
        wpilib.SmartDashboard.putNumber("A3-cm", self.d3.getDistance())


if __name__ == "__main__":
    wpilib.run(MyRobot)
