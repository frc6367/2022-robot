import magicbot
from subsystems.shooter import Shooter
from subsystems.drivetrain import DriveTrain


class SimpleAutonomous(magicbot.AutonomousStateMachine):

    drivetrain: DriveTrain
    shooter: Shooter

    MODE_NAME = "One Ball"
    DEFAULT = False

    @magicbot.timed_state(first=True, duration=3, next_state="backup")
    def shoot(self):
        self.shooter.shoot()

    @magicbot.timed_state(duration=3)
    def backup(self):
        self.drivetrain.move(0.3, 0)
