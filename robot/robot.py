#!/usr/bin/env python3

import wpilib
import magicbot

import ctre
import rev
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A02, SharpIR2Y0A41

from misc.sparksim import CANSparkMax

# import navx


from subsystems.drivetrain import DriveTrain
from subsystems.climber import Climber
from components.climbassistant import ClimbAssistant
from subsystems.intake import Intake
from subsystems.shooter import Shooter


class MyRobot(magicbot.MagicRobot):
    drivetrain: DriveTrain
    climber: Climber
    climb_assistant: ClimbAssistant
    shooter: Shooter
    intake: Intake

    def createObjects(self):
        self.joystick = wpilib.Joystick(0)

        # drivetrain
        self.drive_l1 = ctre.WPI_VictorSPX(1)  #
        self.drive_l2 = ctre.WPI_VictorSPX(2)  #
        self.drive_r1 = ctre.WPI_VictorSPX(3)  #
        self.drive_r2 = ctre.WPI_VictorSPX(4)
        self.encoder_l = wpilib.Encoder(0, 1)
        self.encoder_r = wpilib.Encoder(2, 3)
        # self.nav = navx.AHRS.create_spi()

        # climber
        self.climbSol = wpilib.DoubleSolenoid(wpilib.PneumaticsModuleType.CTREPCM, 6, 7)
        self.compressor = wpilib.Compressor(wpilib.PneumaticsModuleType.CTREPCM)

        # climb assistant
        self.left_bar_sensor = SharpIR2Y0A02(2)
        self.right_bar_sensor = SharpIR2Y0A02(3)

        # intake
        self.belt_motor = CANSparkMax(6, rev.CANSparkMax.MotorType.kBrushless)
        self.intake_motor = ctre.WPI_TalonSRX(7)
        self.entry_sensor = SharpIR2Y0A41(0)
        self.exit_sensor = SharpIR2Y0A41(1)

        # shooter
        self.shooter_motor = CANSparkMax(5, rev.CANSparkMax.MotorType.kBrushless)

        self.blinkies = wpilib.Spark(0)

    def teleopInit(self):
        """Called when teleop starts; optional"""

    def teleopPeriodic(self):
        """Called on each iteration of the control loop"""

        # drivetrain logic goes first
        self.drivetrain.move(self.joystick.getY(), -self.joystick.getX())

        # climber control
        if self.joystick.getRawButtonPressed(5):
            self.climber.raise_hook()

        if self.joystick.getRawButtonPressed(3):
            self.climber.lower_hook()

        if self.joystick.getRawButton(11):
            self.climb_assistant.enableAssist()

        if self.joystick.getRawButton(2):
            self.intake.activate()

        if self.joystick.getRawButton(4):
            self.intake.reverse()

        if self.joystick.getTrigger():
            self.shooter.shoot()


if __name__ == "__main__":
    wpilib.run(MyRobot)
