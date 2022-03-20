import wpilib

if wpilib.RobotBase.isSimulation():

    class CANSparkMax(wpilib.Spark):
        def __init__(self, channel: int, ignored) -> None:
            super().__init__(channel)

else:
    import rev

    CANSparkMax = rev.CANSparkMax
