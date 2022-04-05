import ctre
import wpilib
from misc.sparksim import CANSparkMax
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A21, SharpIR2Y0A41

import enum
import magicbot

from .indicator import Indicator


class IntakeState(enum.Enum):
    OFF = 0
    FWD = 1
    REV = 2


class ReverseState(enum.Enum):
    IDLE = 0
    ENTRY_DETECTED = 1
    DISABLED = 2


class Intake:
    indicator: Indicator

    belt_motor: CANSparkMax
    intake_motor: ctre.WPI_TalonSRX
    entry_sensor: SharpIR2Y0A41
    exit_sensor: SharpIR2Y0A41

    direction = magicbot.will_reset_to(IntakeState.OFF)
    belt_feed_shooter = magicbot.will_reset_to(False)
    intake_force = magicbot.will_reset_to(False)

    entry_threshold = magicbot.tunable(30)
    exit_threshold = magicbot.tunable(30)

    belt_feed_speed = magicbot.tunable(1)
    belt_fwd_speed = magicbot.tunable(0.5)
    belt_fwd_slow_speed = magicbot.tunable(0.4)
    belt_rev_speed = magicbot.tunable(-0.5)

    intake_fwd_speed = magicbot.tunable(0.35)
    intake_rev_speed = magicbot.tunable(-1)

    def __init__(self) -> None:
        self.continue_state = False
        self.reverse_state = ReverseState.IDLE
        self.intake_force_timer = wpilib.Timer()
        self.intake_force_enabled = False

    def on_enable(self):
        if wpilib.DriverStation.isAutonomousEnabled():
            self.intake_force_timer.reset()
            self.intake_force_timer.start()
            self.intake_force_enabled = True
        else:
            self.intake_force_enabled = False

    def activate(self):
        self.direction = IntakeState.FWD

    def force_intake_on(self):
        self.intake_force = True

    def feed_shooter(self):
        self.belt_feed_shooter = True

    def reverse(self):
        self.direction = IntakeState.REV

    @magicbot.feedback
    def get_entry_sensor_distance(self):
        return self.entry_sensor.getDistance()

    @magicbot.feedback
    def get_exit_sensor_distance(self):
        return self.exit_sensor.getDistance()

    @magicbot.feedback
    def is_ball_at_entry(self) -> bool:
        return self.entry_sensor.getDistance() < self.entry_threshold

    @magicbot.feedback
    def is_ball_at_exit(self) -> bool:
        return self.exit_sensor.getDistance() < self.exit_threshold

    def execute(self):

        ball_at_entry = self.is_ball_at_entry()
        ball_at_exit = self.is_ball_at_exit()

        intake_motor_speed = 0
        belt_motor_speed = 0

        # intake stuff
        if self.belt_feed_shooter or self.intake_force:
            if self.belt_feed_shooter:
                belt_motor_speed = self.belt_feed_speed
            if self.intake_force:
                intake_motor_speed = self.intake_fwd_speed
            self.reverse_state = ReverseState.IDLE
        elif self.direction == IntakeState.REV:

            self.continue_state = False

            reverse_state = self.reverse_state

            if reverse_state != ReverseState.DISABLED:
                intake_motor_speed = self.intake_rev_speed
                belt_motor_speed = self.belt_rev_speed

                # only disable reverse after a single ball disappears
                if reverse_state == ReverseState.IDLE:
                    if ball_at_entry:
                        self.reverse_state = ReverseState.ENTRY_DETECTED
                elif reverse_state == ReverseState.ENTRY_DETECTED:
                    if not ball_at_entry:
                        self.reverse_state = ReverseState.DISABLED

                self.indicator.set_reversing()
        else:
            self.reverse_state = ReverseState.IDLE

            if self.direction != IntakeState.FWD:
                intake_motor_speed = 0
            else:
                if ball_at_entry and ball_at_exit:
                    intake_motor_speed = 0
                else:
                    intake_motor_speed = self.intake_fwd_speed

            # belt stuff
            if ball_at_exit:
                if ball_at_entry:
                    self.continue_state = True
                else:
                    self.continue_state = False

                belt_motor_speed = 0

            else:
                if ball_at_entry:
                    self.continue_state = True
                    belt_motor_speed = self.belt_fwd_speed
                    intake_motor_speed = self.intake_fwd_speed
                else:
                    if self.continue_state:
                        # slow the ball down as its getting to the end
                        belt_motor_speed = self.belt_fwd_slow_speed
                    else:
                        belt_motor_speed = 0

            # indicators
            if ball_at_exit and ball_at_entry:
                self.indicator.set_two_balls()
            elif ball_at_exit or ball_at_entry or self.continue_state:
                self.indicator.set_one_ball()

        if self.intake_force_enabled:
            if not self.intake_force_timer.hasElapsed(0.5):
                intake_motor_speed = self.intake_fwd_speed
            else:
                self.intake_force_enabled = False

        self.intake_motor.set(intake_motor_speed)
        self.belt_motor.set(belt_motor_speed)
