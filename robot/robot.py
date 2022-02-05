import wpilib
import ctre
import navx
import magicbot
from subsystems.drivetrain import DriveTrain


class MyRobot(magicbot.MagicRobot):
    drivetrain: DriveTrain

    def createObjects(self):
        self.joystick = wpilib.Joystick(0)
        self.drive_l1 = ctre.WPI_VictorSPX(1)  #
        self.drive_l2 = ctre.WPI_VictorSPX(2)  #
        self.drive_r1 = ctre.WPI_VictorSPX(3)  #
        self.drive_r2 = ctre.WPI_VictorSPX(4)
        self.encoder_l = wpilib.Encoder(0, 1)
        self.encoder_r = wpilib.Encoder(2, 3)
        self.nav = navx.AHRS.create_spi()

    def teleopInit(self):
        """Called when teleop starts; optional"""

    def teleopPeriodic(self):
        """Called on each iteration of the control loop"""
        self.drivetrain.move(self.joystick.getY(), self.joystick.getX())


if __name__ == "__main__":
    wpilib.run(MyRobot)
