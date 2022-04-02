import magicbot

from components.ramsete import RamseteComponent
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from wpimath.trajectory import TrajectoryGenerator


class TDemo(magicbot.AutonomousStateMachine):

    ramsete: RamseteComponent

    MODE_NAME = "TDemo"
    DEFAULT = True

    def on_enable(self) -> None:
        super().on_enable()
        self.tstate = None

    @magicbot.state(first=True)
    def run(self):
        if not self.tstate:
            # Start at the origin facing the +x direction.
            initialPosition = Pose2d(0, 0, Rotation2d(0))

            # Here are the movements we also want to make during this command.
            # These movements should make an "S" like curve.
            movements = [Translation2d(1, 1), Translation2d(2, -1)]

            # End at this position, three meters straight ahead of us, facing forward.
            finalPosition = Pose2d(3, 0, Rotation2d(0))

            # An example trajectory to follow. All of these units are in meters.
            t = TrajectoryGenerator.generateTrajectory(
                initialPosition,
                movements,
                finalPosition,
                self.ramsete.tconfig,
            )

            self.tstate = self.ramsete.startTrajectory(t)
        else:
            if self.tstate.done:
                self.done()
