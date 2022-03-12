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

import wpilib.simulation

from pyfrc.physics.core import PhysicsInterface
from pyfrc.physics import motor_cfgs, tankmodel
from pyfrc.physics.units import units

from wpimath.system import LinearSystemId
from wpimath.system.plant import DCMotor

import typing

if typing.TYPE_CHECKING:
    from robot import MyRobot


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

        # Motors
        self.l_motor = robot.drive_l1.getSimCollection()
        self.r_motor = robot.drive_r1.getSimCollection()

        # TODO: this is probably used elsewhere too
        kV_linear = 1.98
        kA_linear = 0.2
        kV_angular = 1.5
        kA_angular = 0.3

        system = LinearSystemId.identifyDrivetrainSystem(
            kV_linear, kA_linear, kV_angular, kA_angular
        )

        self.drivesim = wpilib.simulation.DifferentialDrivetrainSim(
            system,
            # The robot's trackwidth, which is the distance between the wheels on the left side
            # and those on the right side. The units is meters.
            0.69,
            DCMotor.CIM(4),
            1,
            # The radius of the drivetrain wheels in meters.
            0.15 / 2,
        )

    def update_sim(self, now: float, tm_diff: float) -> None:
        """
        Called when the simulation parameters for the program need to be
        updated.

        :param now: The current time as a float
        :param tm_diff: The amount of time that has passed since the last
                        time that this function was called
        """

        voltage = wpilib.simulation.RoboRioSim.getVInVoltage()

        # Simulate the drivetrain
        self.l_motor.setBusVoltage(voltage)
        l_voltage = self.l_motor.getMotorOutputLeadVoltage()
        r_voltage = -self.r_motor.getMotorOutputLeadVoltage()
        self.drivesim.setInputs(l_voltage, r_voltage)
        self.drivesim.update(tm_diff)

        self.physics_controller.field.setRobotPose(self.drivesim.getPose())
