import math
from tkinter.tix import IMMEDIATE
import typing
import dataclasses

from subsystems.intake import Intake
from components.ramsete import RamseteComponent
from subsystems.shooter import Shooter

import magicbot
import networktables
import wpilib
from wpimath.geometry import Pose2d, Rotation2d, Transform2d
from wpimath.trajectory import TrajectoryGenerator, Trajectory


import constants as c

rdeg = Rotation2d.fromDegrees
tiny_offset = Transform2d(0.1, 0.1, math.radians(-90))


@dataclasses.dataclass
class Action:
    waypoints: typing.Optional[typing.List[Pose2d]] = None
    reverse: bool = False
    intake: bool = False
    reverse_intake: bool = False
    shoot: bool = False
    traj: typing.Optional[Trajectory] = None


class ComplexBase(magicbot.AutonomousStateMachine):

    actions: typing.List[Action]

    ramsete: RamseteComponent
    shooter: Shooter
    intake: Intake

    def setup(self):
        self.idx = -1

        trajectory = Trajectory()

        last_waypoint = None
        for action in self.actions:
            if not action.waypoints:
                continue

            if last_waypoint:
                waypoints = [last_waypoint] + action.waypoints
            else:
                waypoints = action.waypoints

            last_waypoint = waypoints[-1]

            if action.reverse:
                cfg = self.ramsete.tconfig_rev
            else:
                cfg = self.ramsete.tconfig

            action.traj = TrajectoryGenerator.generateTrajectory(waypoints, cfg)
            trajectory += action.traj

        self.ramsete.register_autonomous_trajectory(self.MODE_NAME, trajectory)

    @magicbot.timed_state(first=True, duration=1, next_state="begin_action")
    def init(self):
        """Let the intake drop/settle"""

    @magicbot.state()
    def begin_action(self):
        self.idx += 1
        if len(self.actions) == self.idx:
            self.done()
            return

        self.action = action = self.actions[self.idx]
        if action.shoot:
            self.next_state_now(self.shoot)
        else:
            self.tstate = self.ramsete.startTrajectory(action.traj)
            self.next_state_now(self.driveto)

    @magicbot.state()
    def driveto(self):

        if self.tstate.done:
            self.next_state_now(self.begin_action)
            return

        if self.action.intake:
            self.intake.activate()
        elif self.action.reverse_intake:
            self.intake.reverse()

    @magicbot.timed_state(duration=3, next_state="begin_action")
    def shoot(self):
        self.shooter.shoot()


class ScoreTwoAndDiscard(ComplexBase):
    MODE_NAME = "T: Score Two + Discard Red"
    DEFAULT = False

    actions = [
        Action(
            waypoints=[c.kPose_StartTopStraight, c.kPose_BallTopBlue],
            intake=True,
        ),
        Action(
            waypoints=[c.kPose_BallTopBlue + tiny_offset, c.kPose_ShootTop],
            intake=False,
        ),
        Action(
            shoot=True,
        ),
        Action(
            waypoints=[c.kPose_BallTopRed],
            intake=True,
        ),
        Action(waypoints=[Pose2d(4.4, 11.10, rdeg(-168))], reverse_intake=True),
    ]
