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
    limit = magicbot.will_reset_to(1.0)

    l = magicbot.will_reset_to(0.0)
    r = magicbot.will_reset_to(0.0)
    tank = magicbot.will_reset_to(False)

    lv = magicbot.will_reset_to(0.0)
    rv = magicbot.will_reset_to(0.0)
    volts = magicbot.will_reset_to(False)

    def setup(self):
        self.drive_l1.setInverted(True)
        self.drive_l2.setInverted(True)

        self.drive_l2.follow(self.drive_l1)
        self.drive_r2.follow(self.drive_r1)

        self.drive = wpilib.drive.DifferentialDrive(self.drive_l1, self.drive_r1)

    def limit_speed(self):
        self.limit = 0.5

    def move(self, speed: float, rotation: float):
        self.speed = speed
        self.rotation = rotation

    def tank_drive(self, l, r):
        self.tank = True
        self.l = l
        self.r = r

    def volt_drive(self, lv, rv):
        self.volts = True
        self.lv = lv
        self.rv = rv

    def rotate(self, rotation: float):
        self.rotation = rotation

    def execute(self):
        if self.tank:
            self.drive.tankDrive(self.l, self.r)
        elif self.volts:
            self.drive.feed()
            self.drive_l1.setVoltage(self.lv)
            self.drive_r1.setVoltage(self.rv)
        else:
            self.drive.arcadeDrive(
                self.speed * self.limit, self.rotation * self.limit, False
            )
