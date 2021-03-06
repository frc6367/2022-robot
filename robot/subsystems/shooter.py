from misc.sparksim import CANSparkMax
import magicbot

from .indicator import Indicator
from .intake import Intake


class Shooter(magicbot.StateMachine):
    motor: CANSparkMax
    intake: Intake
    indicator: Indicator

    shooter_speed = magicbot.tunable(0.9)
    ok_speed = magicbot.tunable(4200)
    velocity = magicbot.tunable(0)

    def setup(self):
        self.encoder = self.motor.getEncoder()

    def shoot(self):
        self.engage(initial_state="spinning_up")

    @magicbot.default_state
    def default(self):
        self.motor.set(0)

    @magicbot.timed_state(first=True, duration=0.5, next_state="spun_up")
    def spinning_up(self):
        self.motor.set(self.shooter_speed)
        self.velocity = self.encoder.getVelocity()
        if self.encoder.getVelocity() > self.ok_speed:
            self.next_state("spun_up")

    @magicbot.timed_state(duration=0.5, next_state="shooting_w_belt")
    def spun_up(self):
        self.motor.set(self.shooter_speed)
        self.velocity = self.encoder.getVelocity()
        if self.intake.is_ball_at_exit():
            self.next_state("shooting_w_belt")

    @magicbot.timed_state(
        duration=0.25, must_finish=True, next_state="shooting_no_belt"
    )
    def shooting_w_belt(self):
        self.intake.feed_shooter()
        self.motor.set(self.shooter_speed)
        self.indicator.set_shooting()

    @magicbot.timed_state(duration=0.5, must_finish=True, next_state="spinning_up")
    def shooting_no_belt(self):
        self.motor.set(self.shooter_speed)
        self.indicator.set_shooting()
