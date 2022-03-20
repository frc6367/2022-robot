from sparksim import CANSparkMax
import magicbot

from .intake import Intake


class Shooter(magicbot.StateMachine):
    motor: CANSparkMax
    intake: Intake

    shooter_speed = magicbot.tunable(1)
    ok_speed = magicbot.tunable(1000)

    def setup(self):
        self.encoder = self.motor.getEncoder()

    def shoot(self):
        self.engage(initial_state="spinning_up")

    @magicbot.default_state
    def default(self):
        self.motor.set(0)

    @magicbot.state(first=True)
    def spinning_up(self):
        self.motor.set(self.shooter_speed)
        if self.encoder.getVelocity() > self.ok_speed:
            self.next_state("spun_up")

    @magicbot.state()
    def spun_up(self):
        self.motor.set(self.shooter_speed)

    @magicbot.timed_state(duration=0.5)
    def shooting_w_belt(self):
        self.intake.force_belt_on()
        self.motor.set(self.shooter_speed)

    @magicbot.timed_state(duration=0.5)
    def shooting_no_belt(self):
        self.motor.set(self.shooter_speed)
