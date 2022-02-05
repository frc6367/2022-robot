import wpilib.drive
import ctre
import magicbot


class DriveTrain:
    drive_l1: ctre.WPI_VictorSPX
    drive_l2: ctre.WPI_VictorSPX
    drive_r1: ctre.WPI_VictorSPX
    drive_r2: ctre.WPI_VictorSPX

    speed = magicbot.will_reset_to(0)
    rotation = magicbot.will_reset_to(0)

    def setup(self):
        self.drive_l2.follow(self.drive_l1)
        self.drive_r2.follow(self.drive_r1)

        self.drive = wpilib.drive.DifferentialDrive(self.drive_l1, self.drive_r1)

    def move(self, speed: float, rotation: float):
        self.speed = speed
        self.rotation = rotation

    def execute(self):
        self.drive.arcadeDrive(self.speed, self.rotation, False)
