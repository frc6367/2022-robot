import magicbot
import wpilib
import wpimath.controller
from subsystems.drivetrain import DriveTrain
import navx


class Pointer:
    ahrs: navx.AHRS
    drivetrain: DriveTrain

    kToleranceDegrees = 2.0

    kP = 0.03
    kI = 0.00
    kD = 0.03
    kF = 0.2

    active = magicbot.will_reset_to(False)

    point_debug = magicbot.tunable(False)
    point_at = magicbot.tunable(180)
    max_rotate = magicbot.tunable(0.4)

    @magicbot.feedback
    def yaw(self):
        return self.ahrs.getYaw()

    def setup(self):
        turnController = wpimath.controller.PIDController(
            self.kP,
            self.kI,
            self.kD,
            self.kF,
        )
        turnController.enableContinuousInput(-180.0, 180.0)
        turnController.setTolerance(self.kToleranceDegrees)
        self.turnController = turnController
        wpilib.SmartDashboard.putData("pointer", self.turnController)
        self.last = False

    def reset(self):
        self.ahrs.reset()

    def gotoAngle(self, setpoint: float) -> bool:
        currentRotationRate = -self.turnController.calculate(
            self.ahrs.getYaw(), setpoint
        )
        currentRotationRate = min(
            max(-self.max_rotate, currentRotationRate), self.max_rotate
        )
        self.drivetrain.rotate(currentRotationRate)
        self.active = True
        return self.turnController.atSetpoint()

    def execute(self):
        if self.point_debug:
            if not self.last:
                self.reset()
            self.gotoAngle(self.point_at)
            self.last = True
        else:
            self.last = False

        if not self.active:
            self.turnController.reset()
