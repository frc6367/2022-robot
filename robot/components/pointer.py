import magicbot
import wpilib
import wpimath.controller
from subsystems.drivetrain import DriveTrain
import navx


class Pointer:
    ahrs: navx.AHRS
    drivetrain: DriveTrain

    kToleranceDegrees = 2.0

    if wpilib.RobotBase.isSimulation():
        # These PID parameters are used in simulation
        kP = 0.002
        kI = 0.00
        kD = 0.00
    else:
        # These PID parameters are used on a real robot
        kP = 0.03
        kI = 0.00
        kD = 0.00

    active = magicbot.will_reset_to(False)

    point_debug = magicbot.tunable(False)
    point_at = magicbot.tunable(180)

    @magicbot.feedback
    def yaw(self):
        return self.ahrs.getYaw()

    def setup(self):
        turnController = wpimath.controller.PIDController(
            self.kP,
            self.kI,
            self.kD,
        )
        turnController.enableContinuousInput(-180.0, 180.0)
        turnController.setTolerance(self.kToleranceDegrees)
        self.turnController = turnController
        wpilib.SmartDashboard.putData("pointer", self.turnController)

    def reset(self):
        self.ahrs.reset()

    def gotoAngle(self, setpoint: float) -> bool:
        currentRotationRate = -self.turnController.calculate(
            self.ahrs.getYaw(), setpoint
        )
        self.drivetrain.rotate(currentRotationRate)
        self.active = True
        return self.turnController.atSetpoint()

    def execute(self):
        if self.point_debug:
            self.gotoAngle(self.point_at)

        if not self.active:
            self.turnController.reset()
