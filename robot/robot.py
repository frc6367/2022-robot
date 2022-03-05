import wpilib
import ctre
import magicbot
from subsystems.drivetrain import DriveTrain
from subsystems.climber import Climber


class MyRobot(magicbot.MagicRobot):
    drivetrain: DriveTrain
    climber: Climber

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


if __name__ == "__main__":
    wpilib.run(MyRobot)
