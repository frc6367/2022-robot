import wpilib

if wpilib.RobotBase.isSimulation():

    class SparkMaxRelativeEncoder:
        def getVelocity(self):
            return 0

    class CANSparkMax(wpilib.Spark):
        def __init__(self, channel: int, ignored) -> None:
            super().__init__(channel)

        def getEncoder(self):
            return SparkMaxRelativeEncoder()

else:
    import rev

    CANSparkMax = rev.CANSparkMax
