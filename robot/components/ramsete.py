import navx
import wpilib


import wpimath.controller
import wpimath.kinematics
import wpimath.trajectory
import wpimath.trajectory.constraint


import constants
from subsystems.drivetrain import DriveTrain


class TState:
    done = False


class RamseteComponent:

    drivetrain: DriveTrain
    ahrs: navx.AHRS
    encoder_l: wpilib.Encoder
    encoder_r: wpilib.Encoder

    kP = 8.5
    kI = 0
    kD = 0

    # Baseline values for a RAMSETE follower in units of meters
    # and seconds. These are recommended, but may be changes if wished.
    kRamseteB = 2
    kRamseteZeta = 0.7

    def setup(self) -> None:
        self._state = None

        self._timer = wpilib.Timer()

        print("setup", self.ahrs.getRotation2d())
        self._odometry = wpimath.kinematics.DifferentialDriveOdometry(
            self.ahrs.getRotation2d()
        )

        self._controller = wpimath.controller.RamseteController(
            self.kRamseteB, self.kRamseteZeta
        )

        self._kinematics = wpimath.kinematics.DifferentialDriveKinematics(
            constants.kTrackWidth
        )

        self._ff = wpimath.controller.SimpleMotorFeedforwardMeters(
            constants.kS_linear, constants.kV_linear, constants.kA_linear
        )

        constraint = wpimath.trajectory.constraint.DifferentialDriveVoltageConstraint(
            self._ff, self._kinematics, constants.kMaxVoltage
        )

        self.tconfig = wpimath.trajectory.TrajectoryConfig(
            constants.kMaxSpeedMetersPerSecond,
            constants.kMaxAccelerationMetersPerSecondSquared,
        )
        self.tconfig.setKinematics(self._kinematics)
        self.tconfig.addConstraint(constraint)

        self._l_controller = wpimath.controller.PIDController(self.kP, self.kI, self.kD)
        self._r_controller = wpimath.controller.PIDController(self.kP, self.kI, self.kD)

    def on_disable(self):
        self._state = None

    def startTrajectory(self, trajectory: wpimath.trajectory.Trajectory) -> TState:

        if self._state:
            self._state.done = True

        self._state = TState()
        self._trajectory = trajectory

        initialState = self._trajectory.sample(0)
        self._prevSpeeds = self._kinematics.toWheelSpeeds(
            wpimath.kinematics.ChassisSpeeds(
                initialState.velocity, 0, initialState.velocity * initialState.curvature
            )
        )

        # TODO: probably shouldn't do this here.. oh well
        self._odometry.resetPosition(
            trajectory.initialPose(), self.ahrs.getRotation2d()
        )

        self.encoder_l.reset()
        self.encoder_r.reset()

        self._timer.reset()
        self._timer.start()
        self._lastTm = -1

        self._l_controller.reset()
        self._r_controller.reset()

        return self._state

    def execute(self):

        self._odometry.update(
            self.ahrs.getRotation2d(),
            self.encoder_l.getDistance(),
            self.encoder_r.getDistance(),
        )

        if not self._state:
            return

        now = self._timer.get()
        last_tm = self._lastTm
        dt = now - last_tm

        if last_tm < 0:
            self.drivetrain.volt_drive(0, 0)
            self._lastTm = now
            return

        targetWheelSpeeds = self._kinematics.toWheelSpeeds(
            self._controller.calculate(
                self._odometry.getPose(), self._trajectory.sample(now)
            )
        )

        prevSpeeds = self._prevSpeeds

        lff = self._ff.calculate(
            targetWheelSpeeds.left, (targetWheelSpeeds.left - prevSpeeds.left) / dt
        )
        rff = self._ff.calculate(
            targetWheelSpeeds.right, (targetWheelSpeeds.right - prevSpeeds.right) / dt
        )

        lv = (
            self._l_controller.calculate(
                self.encoder_l.getRate(), targetWheelSpeeds.left
            )
            + lff
        )
        rv = (
            self._r_controller.calculate(
                self.encoder_r.getRate(), targetWheelSpeeds.right
            )
            + rff
        )

        self.drivetrain.volt_drive(-lv, -rv)

        if now > self._trajectory.totalTime():
            self._state.done = True
            self._state = None
            print("final pose", self._odometry.getPose())
        else:
            self._lastTm = now
            self._prevSpeeds = targetWheelSpeeds
