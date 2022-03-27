import wpilib
import magicbot
import enum

from .drivetrain import DriveTrain
from components.bardetect import BarDetect


class ClimbState(enum.Enum):
    RAISED = 0
    LOWERED = 1


class Climber:
    climbSol: wpilib.DoubleSolenoid
    compressor: wpilib.Compressor

    drivetrain: DriveTrain
    bardetect: BarDetect

    nextState = magicbot.will_reset_to(None)

    def __init__(self) -> None:
        self.state = ClimbState.LOWERED

    def raise_hook(self):
        """Raise the climbing hook"""
        self.nextState = ClimbState.RAISED

    def lower_hook(self):
        """Lower the climbing hook"""
        self.nextState = ClimbState.LOWERED

    def execute(self):
        if self.nextState == ClimbState.RAISED:
            self.climbSol.set(wpilib.DoubleSolenoid.Value.kReverse)
            self.state = ClimbState.RAISED
        elif self.nextState == ClimbState.LOWERED:
            self.climbSol.set(wpilib.DoubleSolenoid.Value.kForward)
            self.state = ClimbState.LOWERED
        else:
            self.climbSol.set(wpilib.DoubleSolenoid.Value.kOff)

        if self.state == ClimbState.RAISED:
            self.drivetrain.limit_speed()
            self.bardetect.enable_detector()
            # self.indicator.set_climbing()
