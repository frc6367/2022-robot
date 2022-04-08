import navx
import wpilib
import networktables


import wpimath.controller
import wpimath.kinematics
import wpimath.trajectory
import wpimath.trajectory.constraint


import constants
from subsystems.drivetrain import DriveTrain


class TState:
    done = False


class RamseteComponent:

    autofield: wpilib.Field2d

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

        cconstraint = wpimath.trajectory.constraint.CentripetalAccelerationConstraint(
            constants.kMaxCentripetalAcceleration
        )

        self.tconfig = wpimath.trajectory.TrajectoryConfig(
            constants.kMaxSpeedMetersPerSecond,
            constants.kMaxAccelerationMetersPerSecondSquared,
        )
        self.tconfig.setKinematics(self._kinematics)
        self.tconfig.addConstraint(constraint)
        self.tconfig.addConstraint(cconstraint)

        # reverse constraints... not quite there
        self.tconfig_rev = wpimath.trajectory.TrajectoryConfig(
            constants.kMaxSpeedMetersPerSecond,
            constants.kMaxAccelerationMetersPerSecondSquared,
        )
        self.tconfig_rev.setKinematics(self._kinematics)
        # self.tconfig_rev.addConstraint(constraint)
        self.tconfig_rev.addConstraint(cconstraint)
        self.tconfig_rev.setReversed(True)

        self._l_controller = wpimath.controller.PIDController(self.kP, self.kI, self.kD)
        self._r_controller = wpimath.controller.PIDController(self.kP, self.kI, self.kD)

        self.did_reset = False

    def on_disable(self):
        self._state = None
        self.did_reset = False
        if not RamseteComponent.listener_setup:
            self._setup_trajectory_display()
            RamseteComponent.listener_setup = True

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
        if not self.did_reset:
            self._odometry.resetPosition(
                trajectory.initialPose(), self.ahrs.getRotation2d()
            )

            self.encoder_l.reset()
            self.encoder_r.reset()
            self.did_reset = True

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

        odometryPose = self._odometry.getPose()

        self.autofield.setRobotPose(odometryPose)

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
            self._controller.calculate(odometryPose, self._trajectory.sample(now))
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
        else:
            self._lastTm = now
            self._prevSpeeds = targetWheelSpeeds

    # TODO: these don't really belong here...
    registered_modes = {}
    listener_setup = False

    def register_autonomous_trajectory(self, name, t):
        self.registered_modes[name] = t

    def _setup_trajectory_display(self):
        subtable = networktables.NetworkTables.getTable("SmartDashboard").getSubTable(
            "Autonomous Mode"
        )
        flags = (
            networktables.NetworkTablesInstance.NotifyFlags.NEW
            | networktables.NetworkTablesInstance.NotifyFlags.UPDATE
            | networktables.NetworkTablesInstance.NotifyFlags.IMMEDIATE
        )
        subtable.addEntryListener("selected", self._on_chooser_change, flags)

    def _on_chooser_change(self, table, key, entry, value, flags):
        traj = self.registered_modes.get(value.value())
        tobj = self.autofield.getObject("t")
        if traj:
            tobj.setTrajectory(traj)
        else:
            tobj.setTrajectory(wpimath.trajectory.Trajectory())
