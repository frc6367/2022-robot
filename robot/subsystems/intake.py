import ctre
from misc.sparksim import CANSparkMax
from robotpy_ext.common_drivers.distance_sensors import SharpIR2Y0A21, SharpIR2Y0A41

import enum
import magicbot


class IntakeState(enum.Enum):
    OFF = 0
    FWD = 1
    REV = 2


class Intake:
    belt_motor: CANSparkMax
    intake_motor: ctre.WPI_TalonSRX
    entry_sensor: SharpIR2Y0A41
    exit_sensor: SharpIR2Y0A41

    direction = magicbot.will_reset_to(IntakeState.OFF)
    belt_force = magicbot.will_reset_to(False)

    entry_threshold = magicbot.tunable(30)
    exit_threshold = magicbot.tunable(30)

    belt_fwd_speed = magicbot.tunable(0.5)
    belt_rev_speed = magicbot.tunable(-1)

    intake_fwd_speed = magicbot.tunable(0.3)
    intake_rev_speed = magicbot.tunable(-1)

    def __init__(self) -> None:
        self.continue_state = False

    def activate(self):
        self.direction = IntakeState.FWD

    def force_belt_on(self):
        self.belt_force = True

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
        if self.belt_force:
            belt_motor_speed = self.belt_fwd_speed
        elif self.direction == IntakeState.REV:
            intake_motor_speed = self.intake_rev_speed
            belt_motor_speed = self.belt_rev_speed
            self.continue_state = False
        else:
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
                        belt_motor_speed = self.belt_fwd_speed
                    else:
                        belt_motor_speed = 0

        self.intake_motor.set(intake_motor_speed)
        self.belt_motor.set(belt_motor_speed)
