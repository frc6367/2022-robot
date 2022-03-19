#
# See the documentation for more details on how this works
#
# Documentation can be found at https://robotpy.readthedocs.io/projects/pyfrc/en/latest/physics.html
#
# The idea here is you provide a simulation object that overrides specific
# pieces of WPILib, and modifies motors/sensors accordingly depending on the
# state of the simulation. An example of this would be measuring a motor
# moving for a set period of time, and then changing a limit switch to turn
# on after that period of time. This can help you do more complex simulations
# of your robot code without too much extra effort.
#
# Examples can be found at https://github.com/robotpy/examples

import hal
import wpilib
import wpilib.simulation
from robotpy_ext.common_drivers.distance_sensors_sim import SharpIR2Y0A41Sim

from pyfrc.physics.core import PhysicsInterface
from pyfrc.physics import motor_cfgs, tankmodel
from pyfrc.physics.units import units
import wpimath

from wpimath.system import LinearSystemId
from wpimath.system.plant import DCMotor

import dataclasses
import math
import typing

if typing.TYPE_CHECKING:
    from robot import MyRobot


RED = wpilib.Color8Bit(wpilib.Color.kRed)
BLUE = wpilib.Color8Bit(wpilib.Color.kBlue)
GREEN = wpilib.Color8Bit(wpilib.Color.kGreen)
GRAY = wpilib.Color8Bit(wpilib.Color.kGray)

# wpilib.Color.fromHSV()


@dataclasses.dataclass
class Shape:
    root: wpilib.MechanismRoot2d
    items: typing.List[wpilib.MechanismLigament2d]

    def setPosition(self, x: float, y: float):
        self.root.setPosition(x, y)

    def setColor(self, c: wpilib.Color8Bit):
        for item in self.items:
            item.setColor(c)


class Mechanism(wpilib.Mechanism2d):
    def __init__(self, width: float, height: float) -> None:
        super().__init__(width, height)

    def make_triangle(
        self, name: str, cx: float, cy: float, side: float, line_width=6
    ) -> Shape:
        x = cx + side / 2
        y = cy - side / 2
        root = self.getRoot(name, x, y)
        return self._make(root, side, 120, 3, line_width)

    def make_hex(
        self, name: str, x: float, y: float, side: float, line_width=6
    ) -> Shape:
        # x, y are near bottom right corner
        root = self.getRoot(name, x, y)
        return self._make(root, side, 60, 6, line_width)

    def _make(
        self,
        root: wpilib.MechanismRoot2d,
        side: float,
        angle: float,
        n: int,
        line_width,
    ) -> Shape:
        item = root
        items = []
        for i in range(n):
            item = item.appendLigament(f"{i}", side, angle, line_width)
            items.append(item)

        return Shape(root, items)


BALL_DIAMETER = 9.5
BALL_RADIUS = 4.75


class PhysicsEngine:
    """
    Simulates a 4-wheel robot using Tank Drive joystick control
    """

    def __init__(self, physics_controller: PhysicsInterface, robot: "MyRobot"):
        """
        :param physics_controller: `pyfrc.physics.core.Physics` object
                                   to communicate simulation effects to
        :param robot: your robot object
        """

        self.physics_controller = physics_controller

        # Motors and sensors

        self.entry_sensor = SharpIR2Y0A41Sim(robot.entry_sensor)
        self.exit_sensor = SharpIR2Y0A41Sim(robot.exit_sensor)

        self.entry_motor = wpilib.simulation.PWMSim(robot.entry_motor.getChannel())
        self.belt_motor = wpilib.simulation.PWMSim(robot.belt_motor.getChannel())
        self.shooter_motor = wpilib.simulation.PWMSim(robot.shooter_motor.getChannel())

        self.entry_motor_sim = wpilib.simulation.DCMotorSim(DCMotor.NEO(), 1, 0.0005)
        self.belt_motor_sim = wpilib.simulation.DCMotorSim(DCMotor.NEO(), 1, 0.0005)
        self.shooter_motor_sim = wpilib.simulation.FlywheelSim(DCMotor.NEO(), 4, 0.0005)

        # drawn robot model

        self.model = Mechanism(150, 100)
        wpilib.SmartDashboard.putData("Model", self.model)

        outside = self.model.getRoot("outside", 50, 10)
        l = outside.appendLigament("l1", 50, 0, color=GRAY)
        l = l.appendLigament("l2", 20, 25, color=GRAY)
        l = l.appendLigament("l3", 20, 25, color=GRAY)
        l = l.appendLigament("l4", 20, 25, color=GRAY)
        l = l.appendLigament("l5", 30, 30, color=GRAY)
        l = l.appendLigament("l6", 20, 20, color=GRAY)

        inside = self.model.getRoot("inside", 50, 40)
        inside.appendLigament("l1", 35, 0, color=GRAY)

        shooter = self.model.make_hex("shooter", 105, 40, 15)
        shooter.setColor(BLUE)
        self.shooter = shooter

        self.entry_sensor_pt = self.model.make_triangle("entry-sensor", 50, 25, 3, 2)
        self.exit_sensor_pt = self.model.make_triangle("exit-sensor", 90, 25, 3, 2)

        self.intake_motor_pt = self.model.make_hex("intake-motor", 5, 40, 5, 4)
        self.intake_motor_pt.setColor(GRAY)

        # balls

        # Intake tuning
        self.intake_tuner = hal.SimDevice("Intake Tuner")

        # Represents the end of when the intake motor affects the ball's center
        self.intake_pos_end = self.intake_tuner.createDouble("intake pos end", False, 9)

        # Represents the start/end of when the belt affects the ball's center
        self.belt_pos_start = self.intake_tuner.createDouble("belt pos start", False, 0)
        self.belt_pos_end = self.intake_tuner.createDouble("belt pos end", False, 0)

        # Ball control
        self.ball_device = hal.SimDevice("Balls")
        self.ball_insert = self.ball_device.createBoolean("insert", False, False)

        # The 'value' of each ball is either 'nan' (not present) or it
        # is the distance the ball lies along the track in inches
        self.balls = []

        for i in range(2):
            v = self.ball_device.createDouble(f"center {i}", False, float("nan"))
            m = self.model.make_hex(f"ball {i}", 80, 12, 15, 1)
            m.setColor(RED)

            self.balls.append((v, m))

        # sensor location
        # roller motor
        # belt motor

        # when ball exceeds bounds, if shooter is on, move off scene
        # use sim value to insert ball to scene

        # when belt is moving, set color to red or something

    def update_sim(self, now: float, tm_diff: float) -> None:
        """
        Called when the simulation parameters for the program need to be
        updated.

        :param now: The current time as a float
        :param tm_diff: The amount of time that has passed since the last
                        time that this function was called
        """

        self.intake_simulation(tm_diff)

    def intake_simulation(self, tm_diff: float) -> None:

        # Update motor movement
        v = wpilib.simulation.RoboRioSim.getVInVoltage()
        self.entry_motor_sim.setInputVoltage(self.entry_motor.getSpeed() * v)
        self.entry_motor_sim.update(tm_diff)
        # print(
        #     self.entry_motor_sim.getAngularVelocity()
        # )  # max is 604, whatever that means...

        self.belt_motor_sim.setInputVoltage(self.belt_motor.getSpeed() * v)
        self.belt_motor_sim.update(tm_diff)

        self.shooter_motor_sim.setInputVoltage(self.shooter_motor.getSpeed() * v)
        self.shooter_motor_sim.update(tm_diff)

        # self.shooter_motor_sim.getAngularVelocity()

        #
        # ball movement
        #

        # Has a ball just been inserted?
        if self.ball_insert.value:
            # 'insert' a new ball by setting its position at the starting point
            for ball, _ in self.balls:
                if math.isnan(ball.value):
                    ball.value = 0
                    print("Ball inserted!")
                    break

            self.ball_insert.value = False

        # Valid balls
        balls = [ball for ball in self.balls if not math.isnan(ball[0].value)]

        # Sensors
        self.entry_sensor.setDistance(40)
        self.exit_sensor.setDistance(40)

        ball_positions = []

        for ball, mball in balls:

            #
            # Compute ball movement
            # - if the center of the ball overlaps the range of the specified motor,
            #   then it is moved using the value computed above
            #

            ball_position = ball.value

            #
            # Compute sensor detections
            # - If either edge of the ball lies between the sensors start
            #   or end position, set the voltage appropriately
            #

            # If the ball was shot, remove it
            if ball_position < 0 or ball_position > belt_pos_end:
                print("Ball removed!")
                ball.value = float("nan")

        # Finally, determine if any of the balls overlapped each other
        # - Sort by distance to make it easier to compute ball overlap
        ball_positions = sorted(ball_positions)
        for i in range(1, len(ball_positions)):
            if ball_positions[i] - ball_positions[i - 1] < BALL_DIAMETER:
                print("=" * 72)
                print(" " * 20, "FAIL: balls overlapped!!")
                print(" " * 20, ", ".join("%.3f" % bp for bp in ball_positions))
                print("=" * 72)
                for ball in self.balls:
                    ball.value = float("nan")
                break
