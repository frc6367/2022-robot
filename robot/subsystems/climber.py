import wpilib
import magicbot


class Climber:
    climbSol: wpilib.DoubleSolenoid
    compressor: wpilib.Compressor

    state = magicbot.will_reset_to("off")

    def raise_hook(self):
        """Raise the climbing hook"""
        self.state = "raise"

    def lower_hook(self):
        """Lower the climbing hook"""
        self.state = "lower"

    def execute(self):
        if self.state == "raise":
            self.climbSol.set(wpilib.DoubleSolenoid.Value.kForward)
        elif self.state == "lower":
            self.climbSol.set(wpilib.DoubleSolenoid.Value.kReverse)
        else:
            self.climbSol.set(wpilib.DoubleSolenoid.Value.kOff)
