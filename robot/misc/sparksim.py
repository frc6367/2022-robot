import wpilib

if wpilib.RobotBase.isSimulation():

    class SparkMaxRelativeEncoder:
        def __init__(self) -> None:
            self._velocity = 0

        def getVelocity(self):
            return self._velocity

    class CANSparkMax(wpilib.Spark):
        def __init__(self, channel: int, ignored) -> None:
            super().__init__(channel)
            self._encoder = SparkMaxRelativeEncoder()

        def getEncoder(self):
            return self._encoder

        def setIdleMode(self, mode):
            pass

else:
    import rev

    CANSparkMax = rev.CANSparkMax
