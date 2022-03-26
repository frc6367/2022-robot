import magicbot
from components.pointer import Pointer

from subsystems.intake import Intake
from subsystems.shooter import Shooter
from subsystems.drivetrain import DriveTrain


class TwoBall(magicbot.AutonomousStateMachine):

    drivetrain: DriveTrain
    shooter: Shooter
    intake: Intake
    pointer: Pointer

    MODE_NAME = "Two Ball"
    DEFAULT = True

    # go forward while intaking, 1 second
    @magicbot.timed_state(first=True, duration=1.5, next_state="turnaround")
    def collect_ball(self, initial_call):
        if initial_call:
            self.pointer.reset()

        self.drivetrain.move(-0.3, 0)
        self.intake.activate()

    @magicbot.state()
    def turnaround(self, initial_call):
        if self.pointer.gotoAngle(179.9):
            self.next_state("forward")

    @magicbot.timed_state(duration=3, next_state="shoot")
    def forward(self):
        self.drivetrain.move(-0.3, 0)

    @magicbot.timed_state(duration=3, next_state="backup")
    def shoot(self):
        self.shooter.shoot()

    @magicbot.timed_state(duration=3)
    def backup(self):
        self.drivetrain.move(0.3, 0)
